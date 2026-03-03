#!/usr/bin/env groovy

node('aws&&docker')
{
    // SEC
	withCredentials([
	                 [$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY',
					   credentialsId: 'redteam-aws-cred', secretKeyVariable: 'AWS_SECRET_KEY'],
					 usernamePassword(credentialsId: 'su-dslabs-creds', usernameVariable: 'NEXUS_USR',
					                                                    passwordVariable: 'NEXUS_PWD'),
                     string(credentialsId: 'purple_team_webhook', variable: 'teams_webhook'),
                     string(credentialsId: 'staging-c1ws-api', variable: 'C1WS_API_KEY')
                    ])
    {
        deleteDir()
        parameters {
            string defaultValue: 'dev-eks-1', description: 'EKS Cluster Name',
            name: 'EKS_NAME', trim: true
            string defaultValue: 'us-west-2', description: 'AWS region where eks cluster will be deployed',
            name: 'REGION', trim: true
            string defaultValue: 'us-west2', description: 'SSH Key for corresponding region. Key should be present in deploy_agent folder',
            name: 'KEY_NAME', trim: true
            string defaultValue: 'Cloud Honeypot', description: 'Workload security computer group name',
            name: 'COMP_GRP_NAME', trim: true
            string defaultValue: 'honeypot_deployment', description: 'Nexus component name in dslabs',
            name: 'NEXUS_BASE', trim: true
            string defaultValue: 'https://trendmicro.webhook.office.com/webhookb2/d6c82240-57b1-41b5-84e8-09def3921052@3e04753a-ae5b-42d4-a86d-d6f05460f9e4/JenkinsCI/b131747740c34e90b770e2a911dea18f/5110c51b-5ae9-4caa-a0a8-aafc778ce125',
            description: 'Teams Channel -> "Notifications - Test Notifications" Webhook', name: 'TEAMS_WEBHOOK', trim: true
        }
        def region = params.REGION
        def eks_name = params.EKS_NAME
        def key_name = params.KEY_NAME
        def comp_grp_name = params.COMP_GRP_NAME
        def nexus_base = params.NEXUS_BASE
        def teams_webhook = params.TEAMS_WEBHOOK

        // Common in both Pipeline Variables
        def iac_path="deploy_agent"
        def nexus_url = "https://dsnexus.trendmicro.com/nexus/repository/dslabs/${nexus_base}"
        def dsm_url = "https://staging.deepsecurity.trendmicro.com:443"
        def c1ws_host = "https://staging.deepsecurity.trendmicro.com:443/api"
        def agent_file = "agent.json"

        try
        {
            currentBuild.displayName = "${env.BUILD_NUMBER}"
            currentBuild.result = 'SUCCESS'
            stage('Git checkout')
            {
                // git branch: "${branch}", credentialsId: 'su-dslabs-automation-token',
                //     url: 'https://dsgithub.trendmicro.com/dslabs/honeypot-infra.git'
                checkout scm
            }

            def infraImage = docker.build("infra-image")
            infraImage.inside
            {
                stage('Deploy Agent')
                {
                    // configure aws and kubectl
                    sh "sh setup.sh ${region} ${AWS_ACCESS_KEY} ${AWS_SECRET_KEY} ${eks_name}"
                    sh("aws ec2 describe-instances --region ${region} \
                            --query \"Reservations[*].Instances[*].{PublicIP:PublicIpAddress,SecurityGroups:SecurityGroups[*],Name:Tags[?Key=='Name']|[0].Value,Status:State.Name,hostname:PrivateDnsName}\" \
                            --filters \"Name=instance-state-name,Values=running\" \"Name=tag:Name,Values='*${eks_name}*'\" > ec2.json")

                    sh("python3 src/agent.py --iac_path ${iac_path}                   \
                                             --nexus_url ${nexus_url}/${agent_file}   \
                                             --nexus_cred ${NEXUS_USR} ${NEXUS_PWD}   \
                                             --region ${region}                       \
                                             --key_name ${key_name}                   \
                                             --comp_grp \'${comp_grp_name}\'          \
                                             --c1ws_host ${c1ws_host}                 \
                                             --c1ws_key ${C1WS_API_KEY}               \
                                             --agent_file ${agent_file}")

                    if (fileExists("${agent_file}"))
                    {
                        // agent file
                        agent_file_path = "${WORKSPACE}/${agent_file}"
                        check_file = sh(script: "ls -1 ${agent_file_path}", returnStdout: true).trim()
                        // Delete Existing Eile
                        sh "curl --user $NEXUS_USR:$NEXUS_PWD -X DELETE ${nexus_url}/${agent_file} --fail -v"
                        // Create New File
                        sh "curl --user $NEXUS_USR:$NEXUS_PWD --upload-file ${check_file} ${nexus_url}/${agent_file} --fail -v"

                        stage('Send Teams message')
                        {
                            wrap([$class: 'BuildUser'])
                            {
                                user = "'${env.BUILD_USER_FIRST_NAME} ${env.BUILD_USER_LAST_NAME}'"
                                build_user = "${env.BUILD_USER}"
                                echo "# Build User: ${build_user}"
                            }

                            sh("python src/teams_success.py --nexus_url ${nexus_url}/${agent_file}    \
                                                            --pipeline_type agent                     \
                                                            --teams_webhook ${teams_webhook}          \
                                                            --jenkins_url ${env.BUILD_URL}            \
                                                            --build_user \'${build_user}\'")
                        }
                    }
                }
            }
        }
        catch (e)
        {
            currentBuild.result = 'FAILURE'
            println(e)
            stage('Send Teams message')
            {
                office365ConnectorSend color: '#ff0000',
                                       status: 'FAILURE',
                                       message:  "[Jenkins Build](${env.BUILD_URL})",
                                       webhookUrl: "${teams_webhook}"
            }
        }
    }
}