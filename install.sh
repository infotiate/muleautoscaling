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
