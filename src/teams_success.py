import argparse
import requests
import json


def send_teams_notification(webhook, nexus_url, jenkins_url, build_user):
    message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "00ff00",
        "summary": "EKS Cluster Deployment",
        "sections":
            [
                {
                    "activityTitle": "Cloud HoneyPot - EKS Deployment - {}".format(jenkins_url.split("/")[-2]),
                    "activitySubtitle": "EKS Cluster Deployment",
                    "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
                    "facts":
                        [
                            {
                                "name": "EKS Cluster and Deployment Status",
                                "value": "Success"
                            },
                            {
                                "name": "Build Run By",
                                "value": build_user
                            }
                        ],
                    "markdown": True
                }
            ],
        "potentialAction":
            [
                {
                    "@type": "OpenUri",
                    "name": "Terraform working directory",
                    "targets":
                        [
                            {
                                "os": "default",
                                "uri": nexus_url
                            }
                        ]
                },
                {
                    "@type": "OpenUri",
                    "name": "View Jenkins Build",
                    "targets":
                        [
                            {
                                "os": "default",
                                "uri": jenkins_url
                            }
                        ]
                }
            ]
    }

    headers = {'content-type': 'application/json'}
    requests.post(webhook, data=json.dumps(message), headers=headers)

def send_teams_notification_agent(webhook, nexus_agent, jenkins_url, build_user):
    message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "00ff00",
        "summary": "Agent Deployment in EKS Cluster Node",
        "sections":
            [
                {
                    "activityTitle": "Cloud HoneyPot - Agent Deployment - {}".format(jenkins_url.split("/")[-2]),
                    "activitySubtitle": "Agent Deployment in EKS Cluster Node",
                    "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
                    "facts":
                        [
                            {
                                "name": "Agent Deployment Status",
                                "value": "Success"
                            },
                            {
                                "name": "Build Run By",
                                "value": build_user
                            }
                        ],
                    "markdown": True
                }
            ],
        "potentialAction":
            [
                {
                    "@type": "OpenUri",
                    "name": "Agent Tracking file",
                    "targets":
                        [
                            {
                                "os": "default",
                                "uri": nexus_agent
                            }
                        ]
                },
                {
                    "@type": "OpenUri",
                    "name": "View Jenkins Build",
                    "targets":
                        [
                            {
                                "os": "default",
                                "uri": jenkins_url
                            }
                        ]
                }
            ]
    }

    headers = {'content-type': 'application/json'}
    requests.post(webhook, data=json.dumps(message), headers=headers)

def send_teams_notification_destroy(webhook, jenkins_url, build_user):
    message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "00ff00",
        "summary": "EKS Destruction",
        "sections":
            [
                {
                    "activityTitle": "Cloud HoneyPot - EKS Destroy - {}".format(jenkins_url.split("/")[-2]),
                    "activitySubtitle": "EKS Destroy Notification",
                    "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
                    "facts":
                        [
                            {
                                "name": "EKS Destroy Status",
                                "value": "Success"
                            },
                            {
                                "name": "Build Run By",
                                "value": build_user
                            }
                        ],
                    "markdown": True
                }
            ],
        "potentialAction":
            [
                {
                    "@type": "OpenUri",
                    "name": "View Jenkins Build",
                    "targets":
                        [
                            {
                                "os": "default",
                                "uri": jenkins_url
                            }
                        ]
                }
            ]
    }

    headers = {'content-type': 'application/json'}
    requests.post(webhook, data=json.dumps(message), headers=headers)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--nexus_url", type=str, help="Nexus URL")
    parser.add_argument("--pipeline_type", type=str, help="Pipeline type")
    parser.add_argument("--teams_webhook", type=str, help="Teams Webhook URL")
    parser.add_argument("--jenkins_url", type=str, help="Jenkins URL")
    parser.add_argument("--build_user", type=str, help="Build User")
    args = parser.parse_args()

    if args.pipeline_type == "deploy":
        send_teams_notification(args.teams_webhook, args.nexus_url, args.jenkins_url, args.build_user)
    elif args.pipeline_type == "agent":
        send_teams_notification_agent(args.teams_webhook, args.nexus_url, args.jenkins_url, args.build_user)
    elif args.pipeline_type == "destroy":
        send_teams_notification_destroy(args.teams_webhook, args.jenkins_url, args.build_user)