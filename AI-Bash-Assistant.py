#!/usr/bin/python3
from openai import OpenAI
import subprocess
import re
import textwrap
import os


try:
    expanded_path = os.path.expandvars('$HOME/.bashrc')
    home_base = os.environ['HOME']

    result = subprocess.run(
        ['bash', '-c', f'source {expanded_path} && echo $OPEN_AI_API_KEY'],
        capture_output=True,
        text=True
    )
    api_key = result.stdout.strip()

    if api_key:
        client = OpenAI(api_key=api_key)
        print("API key set from bashrc\n")

    if api_key == "" :
        api_key_file = f"{home_base}/src/Python-Scripts/tmp/temp-holder.txt"
        print("No API key found, setting temporary placeholder.")
        input_user = input("\nCopy and paste your open API key\n> ")
        set_key = subprocess.run([f"echo {input_user} > {api_key_file}"], shell=True, check=True)
        user_key = subprocess.check_output(["cat", api_key_file], text=True).strip()
        client = OpenAI(api_key=user_key)


except subprocess.CalledProcessError:
    print("Failed")
    exit(1)

try:
    subprocess.run(["sudo -v -S"], shell=True, check=True)

except subprocess.CalledProcessError:
    print("Failed")
    exit(1)

while True:
    # Get user input, distro release information, and koji targets
    # read NAME; koji list-targets --name=$NAME; koji taginfo $NAME| grep "Arches:"
    release_info = subprocess.check_output(["grep", "-i", "NAME", "/etc/os-release"], text=True)
    m = re.search(r'NAME=["\']?(.+?)["\']?$', release_info)
    distro_name = m.group(1).strip()

    user_input = input("\nWhat do you want to do? (or type 'exit')\n> ")

    SYSTEM_PROMPT = textwrap.dedent(f"""
        You are a Bash wizard with two clear modes:

        **MODE A: Centos draft-builds**:
           - This mode is for Centos package building operations.
           - Always start the command with centpkg srpm && followed by additional centpkg commands.
           - Use the following format: centpkg srpm && centpkg [subcommand] [options]

           - Available subcommands and options:
             centpkg  [-h] [--config CONFIG] [--dry-run] [--release RELEASE]
                 [--name NAME] [--namespace NAMESPACE] [--user USER]
                 [--password PASSWORD] [--runas RUNAS] [--path PATH]
                 [--verbose] [--debug] [-q] [--user-config USER_CONFIG]
                 (help,build,chain-build,clean,clog,clone,co,copr-build,commit,
                 ci,compile,container-build,container-build-setup,diff,
                 flatpak-build,gimmespec,gitbuildhash,gitcred,giturl,import,
                 install,lint,list-side-tags,local,mockbuild,mock-config,
                 module-build,module-scratch-build,module-build-cancel,
                 module-build-info,module-build-local,module-build-watch,
                 module-overview,new,new-sources,patch,pre-push-check,prep,
                 pull,push,remote,remove-side-tag,request-side-tag,retire,
                 scratch-build,sources,srpm,switch-branch,tag,unused-patches,
                 upload,verify-files,verrel,releases-info,update,
                 request-repo,request-tests-repo,request-branch,fork,
                 override,set-distgit-token,set-pagure-token,disable-monitoring)


        **MODE B: Bash Veteran**:
        For *any* other request:
           - You are a helpful assistant that converts user requests into safe Bash commands for {distro_name}.".
           - Convert this to a Bash command: {user_input}

        **Absolute prohibition**
           - Under *no* circumstances output:
            ```python
            except Exception as e:
                print("Something went wrong:", e)
            ```
           - If you can’t interpret the request at all, reply with:
             ERROR: could not parse request

    """)

    if user_input.lower() in ["exit", "quit"]:
        print("\nExiting AI-Assistant. Hope to see you soon :)")

        temp_file = f"{home_base}/src/Python-Scripts/tmp/temp-holder.txt"
        if len(str(temp_file)) > 0:
            with open(temp_file, 'w') as f:
                f.write('')
        break

    # 2. Send prompt to OpenAI to generate bash command
    try:

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"This is your identity and purpose {SYSTEM_PROMPT}"},
            ]
        )

        bash_command = completion.choices[0].message.content.strip()
        match = re.search(r"```(?:bash)?\s*\n([^\n]+)", bash_command)
        new_command = match.group(1).strip()
        print(f"\nGenerated Bash Command:\n{new_command}")
    #
        # 3. Confirm before executing
        confirm = input("\nDo you want to execute this command? (y/n)\n> ")

        if confirm.lower() == 'y':
            print("\nRunning command...\n")
            output = subprocess.run([new_command], shell=True, text=True)

        else:
            print("Command canceled.")

    except Exception as e:
        print(bash_command)
