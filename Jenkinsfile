#!groovy

node('aws&&docker')
{
    // SEC
	withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY',
					   credentialsId: 'redteam-aws-cred', secretKeyVariable: 'AWS_SECRET_KEY'],
					usernamePassword(credentialsId: 'c1ws_cred', usernameVariable: 'C1WS_USR',
					                                             passwordVariable: 'C1WS_PWD'),
					usernamePassword(credentialsId: 'su-dslabs-creds', usernameVariable: 'NEXUS_USR',
					                                                    passwordVariable: 'NEXUS_PWD'),
				    string(credentialsId: 'purple_team_webhook', variable: 'teams_webhook')])
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
            string defaultValue: 'EKS-Destroy', description: 'Trigger EKS Cluster Destroy pipeline',
            name: 'DESTROY_PIPELINE', trim: true
            booleanParam defaultValue: false, description: 'To skip the destroy EKS cluster pipeline',
            name: 'SKIP_DESTROY_PIPELINE'
            string defaultValue: 'deploy-agent', description: 'Trigger agent installation pipeline',
            name: 'DEPLOY_AGENT', trim: true
            string defaultValue: 'honeypot_deployment', description: 'Nexus component name in dslabs',
            name: 'NEXUS_BASE', trim: true
            string defaultValue: 'https://trendmicro.webhook.office.com/webhookb2/d6c82240-57b1-41b5-84e8-09def3921052@3e04753a-ae5b-42d4-a86d-d6f05460f9e4/JenkinsCI/b131747740c34e90b770e2a911dea18f/5110c51b-5ae9-4caa-a0a8-aafc778ce125',
            description: 'Teams Channel -> "Notifications - Test Notifications" Webhook', name: 'TEAMS_WEBHOOK', trim: true
        }

        def region = params.REGION
        def eks_name = params.EKS_NAME
        def key_name = params.KEY_NAME
        def comp_grp_name = params.COMP_GRP_NAME
        def destroy_pipeline = params.DESTROY_PIPELINE
        def skip_destroy_pipeline = params.SKIP_DESTROY_PIPELINE
        def deploy_agent = params.DEPLOY_AGENT
        def nexus_base = params.NEXUS_BASE
        def teams_webhook = params.TEAMS_WEBHOOK

        // Common in both Pipeline Variables
        def iac_path="eks_4.6.0"
        def nexus_url = "https://dsnexus.trendmicro.com/nexus/repository/dslabs/${nexus_base}"
        def tf_working_dir = "${iac_path}.zip"
        def destroy_file = "main.destroy.tfplan"
        def tf_working_dir_url = ""

        try
        {
            currentBuild.displayName = "${env.BUILD_NUMBER}"
            currentBuild.result = 'SUCCESS'
            stage('Git checkout')
            {
                checkout scm
            }
            // dynamic variables setup for terraform
            def job_name = "${env.JOB_BASE_NAME}"
            def dev_pipeline = "test"
            def prod_var = "variables.tf"
            def dev_var = "test-variables.tf"

            stage('Prepare terraform varibale')
            {
                echo "${job_name}"
                if (job_name.contains("${dev_pipeline}"))
                {
                    echo "Development Pipeline ${job_name}"
                    sh "rm ${iac_path}/${prod_var}"
                }
                else
                {
                    echo "Production Pipeline ${job_name}"
                    sh "rm ${iac_path}/${dev_var}"
                }
            }
            if ("${skip_destroy_pipeline}" == "false")
            {
                stage('Destroy Cluster Pipeline')
                {
                    agent_job = build job: "${destroy_pipeline}",
                        parameters: [
                            string(name: 'EKS_NAME', value: "${eks_name}"),
                            string(name: 'REGION', value: "${region}"),
                            string(name: 'COMP_GRP_NAME', value: "${comp_grp_name}"),
                            string(name: 'NEXUS_BASE', value: "${nexus_base}"),
                            string(name: 'TEAMS_WEBHOOK', value: "${teams_webhook}")
                        ]
                }
            }

            def infraImage = docker.build("infra-image")
            infraImage.inside
            {
                stage('Create Infra')
                {
                    sh "sh main.sh ${region} ${AWS_ACCESS_KEY} ${AWS_SECRET_KEY} ${eks_name} ${iac_path} ${destroy_file} ${key_name}"
                }
                stage('Restore destroy plan')
                {
                    sh "zip -r ${tf_working_dir} ${iac_path}"
                    if (fileExists("${tf_working_dir}"))
                    {
                        // https://learn.hashicorp.com/tutorials/terraform/automate-terraform#plan-and-apply-on-different-machines
                        // destroy plan
                        tf_working_dir_url = "${nexus_url}/${tf_working_dir}"
                        int des_status_code = sh(script: "curl -u ${NEXUS_USR}:${NEXUS_PWD} -sLI -w '%{http_code}' $tf_working_dir_url -o /dev/null", returnStdout: true)
                        echo "${tf_working_dir_url} status code: ${des_status_code}"
                        if (des_status_code != 404)
                        {
                            // Delete Existing Eile
                            sh "curl --user $NEXUS_USR:$NEXUS_PWD -X DELETE ${tf_working_dir_url} --fail -v"
                        }
                        // Create New File
                        sh "curl --user $NEXUS_USR:$NEXUS_PWD --upload-file ${tf_working_dir} ${tf_working_dir_url} --fail -v"
                    }
                    else
                    {
                        throw new Exception("${destroy_file} not Found!")
                    }
                }
                stage('Send Teams message')
                {
                    wrap([$class: 'BuildUser'])
                    {
                        user = "'${env.BUILD_USER_FIRST_NAME} ${env.BUILD_USER_LAST_NAME}'"
                        build_user = "${env.BUILD_USER}"
                        echo "# Build User: ${build_user}"
                    }

                    sh("python src/teams_success.py --nexus_url ${tf_working_dir_url}   \
                                                    --pipeline_type deploy              \
                                                    --teams_webhook ${teams_webhook}    \
                                                    --jenkins_url ${env.BUILD_URL}      \
                                                    --build_user \'${build_user}\'")
                }
                stage('Deploy Agent Pipeline')
                {
                    agent_job = build job: "${deploy_agent}",
						        parameters: [
							        string(name: 'EKS_NAME', value: "${eks_name}"),
							        string(name: 'REGION', value: "${region}"),
							        string(name: 'KEY_NAME', value: "${key_name}"),
							        string(name: 'COMP_GRP_NAME', value: "${comp_grp_name}"),
							        string(name: 'NEXUS_BASE', value: "${nexus_base}"),
							        string(name: 'TEAMS_WEBHOOK', value: "${teams_webhook}")
						        ]
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
        finally
        {
            archiveArtifacts allowEmptyArchive: true, artifacts: "${tf_working_dir}"
        }
    }
}
