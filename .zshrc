export PATH="$HOME/.cargo/bin:$PATH"

# Comment out Miniforge initialization
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
#__conda_setup="$('/Users/md/miniforge3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
#if [ $? -eq 0 ]; then
#    eval "$__conda_setup"
#else
#    if [ -f "/Users/md/miniforge3/etc/profile.d/conda.sh" ]; then
#        . "/Users/md/miniforge3/etc/profile.d/conda.sh"
#    else
#        export PATH="/Users/md/miniforge3/bin:$PATH"
#    fi
#fi
#unset __conda_setup
# <<< conda initialize <<<

# Add Anaconda initialization
export PATH="/opt/anaconda3/bin:$PATH"
. /opt/anaconda3/etc/profile.d/conda.sh

# Keep your existing paths
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

export PATH="$PATH:/Users/md/.local/bin"
export PATH="/Users/md/.local/bin:$PATH"

export PATH="/opt/homebrew/bin:$PATH" 