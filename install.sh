#!/bin/bash 
echo 'Usage ./install.sh <<s3 bucket name>>'
SAM_S3_BUCKET=$1

echo 'Updating the system...'
sudo yum update -y
echo 'Installing git'
sudo yum install git -y
echo 'Installing HomeBrew for SAM'
sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"
brew --version

echo 'Adding Homebrew to your PATH'
test -d ~/.linuxbrew && eval $(~/.linuxbrew/bin/brew shellenv)
test -d /home/linuxbrew/.linuxbrew && eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
test -r ~/.bash_profile && echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.bash_profile
echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.profile

echo 'Installing AWS SAM CLI'
brew tap aws/tap
brew install aws-sam-cli

sam --version
echo 'Installation Successful'

echo 'Cloning Infotiate muleautoscaling git repo'
git clone https://github.com/infotiate/muleautoscaling.git
cd muleautoscaling

echo 'Building the code'
sam build

echo 'Packaging...'
chmod +x ./package.sh
./package.sh muleasg $SAM_S3_BUCKET
