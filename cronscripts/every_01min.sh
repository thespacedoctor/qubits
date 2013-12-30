#! /bin/sh

# If a git repo update request has been issued then update now
if [ -f /home/dry/cron_requests/update_qubits ]
then
    echo "
    # updating git repos "
    echo "----------------------------------------------"
    rm -f /home/dry/cron_requests/update_qubits
    dcu_update_git_repos --settingsFile=/home/dry/github_repos/qubits/settings/qubit_github.yaml
fi
