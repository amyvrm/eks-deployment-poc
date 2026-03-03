#!/usr/bin/env groovy

node('aws&&docker')
{
    // SEC
	withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY',
					   credentialsId: 'redteam-aws-cred', secretKeyVariable: 'AWS_SECRET_KEY'],
					usernamePassword(credentialsId: 'c1ws_cred', usernameVariable: 'C1WS_USR',
					                                             passwordVariable: 'C1WS_PWD'),
					usernamePassword(credentialsId: 'su-dslabs-creds', usernameVariable: 'NEXUS_USR',
					                                                    passwordVariable: 'NEXUS_PWD'),
				    string(credentialsId: 'purple_team_webhook', variable: 'teams_webhook'),
				    string(credentialsId: 'staging-c1ws-api', variable: 'C1WS_API_KEY')])
    {
        deleteDir()
        parameters {
            string defaultValue: 'dev-eks-1', description: 'EKS Cluster Name',
            name: 'EKS_NAME', trim: true
            string defaultValue: 'us-west-2', description: 'AWS region where eks cluster will be deployed',
            name: 'REGION', trim: true
            string defaultValue: 'Cloud Honeypot', description: 'Workload security computer group name',
            name: 'COMP_GRP_NAME', trim: true
            string defaultValue: 'honeypot_deployment', description: 'Nexus component name in dslabs',
            name: 'NEXUS_BASE', trim: true
            string defaultValue: 'https://trendmicro.webhook.office.com/webhookb2/d6c82240-57b1-41b5-84e8-09def3921052@3e04753a-ae5b-42d4-a86d-d6f05460f9e4/JenkinsCI/b131747740c34e90b770e2a911dea18f/5110c51b-5ae9-4caa-a0a8-aafc778ce125',
            description: 'Teams Channel -> "Notifications - Test Notifications" Webhook', name: 'TEAMS_WEBHOOK', trim: true
        }
        def region = params.REGION
        def eks_name = params.EKS_NAME
        def comp_grp_name = params.COMP_GRP_NAME
        def nexus_base = params.NEXUS_BASE
        def teams_webhook = params.TEAMS_WEBHOOK

        // Common in both Pipeline Variables
        def iac_path="eks_4.6.0"
        def nexus_url = "https://dsnexus.trendmicro.com/nexus/repository/dslabs/${nexus_base}"
        def tf_working_dir = "${iac_path}.zip"
        def destroy_file = "main.destroy.tfplan"
        def c1ws_host = "https://staging.deepsecurity.trendmicro.com:443/api"
        def api_version = "v1"
        def agent_file = "agent.json"

        try
        {
            currentBuild.displayName = "${env.BUILD_NUMBER}"
            currentBuild.result = 'SUCCESS'
            stage('Git checkout')
            {
                checkout scm
            }

            def infraImage = docker.build("infra-image")
            infraImage.inside
            {
                stage('Destroy infra')
                {
                    // configure aws and kubectl
                    sh "sh setup.sh ${region} ${AWS_ACCESS_KEY} ${AWS_SECRET_KEY} ${eks_name}"

                    // https://learn.hashicorp.com/tutorials/terraform/automate-terraform#plan-and-apply-on-different-machines
                    // fetch terraform working directory
                    sh "rm -rf ${iac_path}"
                    sh "curl --user $NEXUS_USR:$NEXUS_PWD ${nexus_url}/${tf_working_dir} --output ${tf_working_dir} --fail -v"
                    sh "unzip ${tf_working_dir}"
                    sh "sh destroy.sh ${iac_path} ${destroy_file}"
                }
                stage('Clear the agent.json file')
                {
                     sh("python src/empty_agent_json_file.py --nexus_url ${nexus_url}/${agent_file}     \
                                                             --nexus_cred ${NEXUS_USR} ${NEXUS_PWD}")
                }
                stage('Remove agents from workload security')
                {
                    echo "# Commented code to remove agent from C1WS"
//                      sh("python src/agent_operation.py --c1ws_host ${c1ws_host}                   \
//                                                        --c1ws_key ${C1WS_API_KEY}                 \
//                                                        --version ${api_version}                   \
//                                                        --del_comp_grp \'${comp_grp_name}\'        \
//                                                        --nexus_url ${nexus_url}/${agent_file}     \
//                                                        --nexus_cred ${NEXUS_USR} ${NEXUS_PWD}")
                }
                stage('Send Teams message')
                {
                    wrap([$class: 'BuildUser'])
                    {
                        user = "'${env.BUILD_USER_FIRST_NAME} ${env.BUILD_USER_LAST_NAME}'"
                        build_user = "${env.BUILD_USER}"
                        echo "# Build User: ${build_user}"
                    }

                    sh("python src/teams_success.py --nexus_url ${nexus_url}             \
                                                    --pipeline_type destroy              \
                                                    --teams_webhook ${teams_webhook}     \
                                                    --jenkins_url ${env.BUILD_URL}       \
                                                    --build_user \'${build_user}\'")
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
