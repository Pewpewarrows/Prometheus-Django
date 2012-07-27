#!/usr/bin/env sh

# Avoid double inclusion
if [[ "${BashInclude__imported+defined}" == "defined" ]]; then
    return 0
fi
BashInclude__imported=1

Bootstrap__os=Linux
case `uname` in
    Darwin)
        Bootstrap__os=Darwin
        ;;
esac

# For a good example of why you should never upgrade a system-default
# interpreter for a dynamic language:
#
#   find /usr -name '*.rb'
#   find /usr -name '*.py'
#
# Those are program files that depend on the version of ruby/python that comes
# with your OS. Upgrading the system-default interpreter will introduce
# backwards-incompatibilities that can and will bring those programs to a halt.
# Instead, use tools like rvm, rbenv, and pythonbrew to manage user / project
# installations of those languages.

function Bootstrap__silent_cmd {
    local command_line="$1"

    `${command_line} >/dev/null 2>&1`
}

function Bootstrap__is_available {
    local command_name="$1"

    Bootstrap__silent_cmd "command -v ${command_name}"
}

function Bootstrap__check_for_progs {
    local missing=() prog

    for prog; do
        if ! Bootstrap__is_available "$prog"; then
            missing+=("$prog")
        fi
    done

    if (( ${#missing[@]} )); then
        echo >&2 "$0: the following required commands were not found:"
        printf >&2 "\t%s\n" "${missing[@]}"
        return 1
    fi

    return 0
}

function Bootstrap__python_available {
    # TODO: version argument

    local exit_on_failure="${1:-true}"

    if ! Bootstrap__is_available "python"; then
        echo "Please install the latest version of Python available for your OS."

        if $exit_on_failure; then
            exit
        fi

        return 1
    fi

    return 0
}

function Bootstrap__ruby_available {
    # TODO: version argument
    Bootstrap__is_available "ruby"
}

function Bootstrap__pythonbrew_available {
    # TODO: version argument
    local exit_on_failure="${1:-true}"

    if ! Bootstrap__is_available "pythonbrew"; then
        echo "Pythonbrew not found. Follow the installation instructions here: https://github.com/utahta/pythonbrew/"

        if $exit_on_failure; then
            exit
        fi

        return 1
    fi

    return 0
}

function Bootstrap__python_version {
    # TODO: better version argument parsing

    local python_ver="$1"

    local actual_python_ver=`python -V 2>&1`
    actual_python_ver=${actual_python_ver/"Python "/""}

    if [[ "${python_ver}" != "${actual_python_ver}" ]]; then
        echo "This virtualenv has the wrong python version (${actual_python_ver}). Please run \`pybrew install ${python_ver}\` and rebuild this virtualenv to proceed."

        if $exit_on_failure; then
            exit
        fi

        return 1
    fi

    return 0
}

function Bootstrap__in_virtualenv {
    # TODO: detect when inside a different virtualenv than argument

    local venv_name="$1"
    local exit_on_failure="${2:-true}"

    local is_venv=`python -c "import sys; print hasattr(sys, 'real_prefix')"`

    if [[ "${is_venv}" == "False" ]]; then
        echo "Please run: \`pybrew venv use ${venv_name}\`"

        if $exit_on_failure; then
            exit
        fi

        return 1
    fi

    return 0
}

function Bootstrap__install_python_libs {
    local req_file="$1"

    local curdir=${0%/*}

    pushd `dirname $0` > /dev/null
    local abspath=`pwd -P`
    popd > /dev/null

    pip install -r ${curdir}/../conf/requirements/develop.txt --no-index -f file://${abspath}/../vendor/python/
}

# Pip
# PyBrew Python Version
# PyBrew Virtualenv
# Virtualenv Requirements
# Gem bundle
# Rbenv
# Node.js
# NPM stuff
# Java
# Maven
# Scala
# Clojure
# PHP
# Some PHP virtualenv solution
# Lisp/Scheme/Lua/Smalltalk?
# C/C++/C#/Obj-C
# .NET/Mono

# Sqlite
# Postgres
# Mysql
# MongoDB
# Memcached
# Redis
# Riak
# Varnish
# Nginx/Apache

# Git/Hg hooks
# Tmux/tmuxinator stuff?
# Vagrant?
