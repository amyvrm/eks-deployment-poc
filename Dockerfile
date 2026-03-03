FROM python
RUN apt-get update
RUN useradd -s /bin/bash -u 501 -U -d /build -m build && groupmod -g 501 build

# terraform https://learn.hashicorp.com/tutorials/terraform/install-cli
RUN apt-get install -y gnupg software-properties-common curl
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -
RUN apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
RUN apt-get update
RUN apt-get install terraform=1.1.7
#RUN apt-get install terraform=1.1.8

# aws cli https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# kubectl https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
RUN apt-get install -y apt-transport-https ca-certificates
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update
RUN apt-get install -y kubectl
RUN kubectl version --client

RUN apt-get install -y less
RUN apt-get install -y python3-pip python3-dev
RUN pip3 install zeep
RUN pip3 install urllib3
RUN pip3 install requests

# c1cs deployment
RUN curl https://baltocdn.com/helm/signing.asc | apt-key add -
RUN apt-get install apt-transport-https --yes
RUN echo "deb https://baltocdn.com/helm/stable/debian/ all main" | tee RUN /etc/apt/sources.list.d/helm-stable-debian.list
RUN apt-get update
RUN apt-get install helm
RUN apt install zip