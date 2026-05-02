#!/usr/bin/python3
from time import sleep
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

    if api_key == "":
        api_key_file = "/home/src/AI-Bash-Assistant-Prototype/temp-holder.txt"
        print("No API key found, setting temporary placeholder.")
        input_user = input("\nCopy and paste your open API key\n> ")
        set_key = subprocess.run([f"echo {input_user} > {api_key_file}"], shell=True, check=True)
        user_key = subprocess.check_output(["cat", api_key_file], text=True).strip()
        client = OpenAI(api_key=user_key)


except subprocess.CalledProcessError:
    print("Failed subprocess call")

try:
    subprocess.run(["sudo -v -S"], shell=True, check=True)

except subprocess.CalledProcessError:
    print("Failed subprocess call")
    exit(1)

while True:
    try:
        release_info = subprocess.check_output(["grep", "-i", "NAME", "/etc/os-release"], text=True)
        m = re.search(r'NAME=["\']?(.+?)["\']?$', release_info)
        distro_name = m.group(1).strip()

        user_input = input("\nWhat do you want to do? (or type 'exit')\n> ")

        MODE_A = textwrap.dedent(f"""
            You are a Bash wizard with 2 clear modes:

            **MODE A: Bash Veteran**:
            For *any* request:
               - You are a helpful assistant that converts user requests into safe Bash commands for {distro_name}.".
               - Convert this to a Bash command: {user_input}
               - Make sure the bash command aligns with the users {distro_name}  


            **MODE B: Error handling / retry behavior**
            For *any* request after input is prompted:
            - Never return raw system errors, stack traces, or generic failure messages such as:
              "Something went wrong:"

            - If the user request is unclear, incomplete, or fails on the first interpretation:
              1. Re-read the original user input.
              2. Try to infer the most likely intent.
              3. Retry the task once using that interpretation.
              4. Do not ask the user for clarification unless there is no reasonable interpretation.

            - The wizard should always attempt a useful response before giving up.

        """)
        
        if user_input.lower() in ["scratch build", "kernel build", "mock build",
                                  "scratch-build", "kernel-build", "mock-build",
                                  "scratchbuild", "kernelbuild", "mockbuild"]:
            
            

            print("\nPick one from the list below\n")
            subprocess.run(["koji list-targets"], shell=True, check=True)

            sleep(3)

            target = input("\nPaste your pick\n")
            subprocess.run([f'NAME={target} && koji list-targets --name=$NAME'], shell=True, text=True)

            print("\n")
            print("Copy an arch from below\n")

            subprocess.run(["../arches.sh"])
            arches = input("\nPaste your pick\n")

            MODE_B = textwrap.dedent(f"""
                You are a Bash wizard with 2 clear modes:

                **MODE A: Fedora draft-builds**:

                For *any* request:
                   - You are a helpful assistant that converts user requests into safe Bash commands
                   - This mode is for Fedora kernel/package building operations.
                   - Do not invent or assume a build target that was not returned by {target}.
                   - Always start the command with fedpkg srpm && followed by additional fedpkg commands.
                   - Use the following format: fedpkg srpm && fedpkg scratch-build --target {target} --arches {arches}
                   - Make sure the bash command aligns with the users {distro_name} 

                   - Available subcommands and options:
                     fedpkg mockbuild [-h] [--config CONFIG] [--dry-run] [--release RELEASE]
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

                **MODE B: Error handling / retry behavior**
                For *any* request after input is prompted:
                - Never return raw system errors, stack traces, or generic failure messages such as:
                  "Something went wrong:"

                - If the user request is unclear, incomplete, or fails on the first interpretation:
                  1. Re-read the original user input.
                  2. Try to infer the most likely intent.
                  3. Retry the task once using that interpretation.
                  4. Do not ask the user for clarification unless there is no reasonable interpretation.

                - The wizard should always attempt a useful response before giving up.

                         """)

            completion = client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": f"This is your identity and purpose {MODE_B}"},
                ]
            )

            build_command = completion.choices[0].message.content.strip()
            matched = re.search(r"```(?:bash)?\s*\n([^\n]+)", build_command)

            submit_command = matched.group(1).strip()
            print(f"\nGenerated Bash Command:\n{submit_command}")

            # 3. Confirm before executing
            confirm = input("\nDo you want to execute this command? (y/n)\n> ")

            if confirm.lower() == 'y':
                print("\nRunning command\n")
                output = subprocess.run([submit_command], shell=True, text=True)

            else:
                print("Command canceled.")
                
        if user_input.lower() in ["exit", "quit"]:
            print("\nExiting AI-Assistant. Hope to see you soon :)")

            temp_file = "/home/src/AI-Bash-Assistant-Prototype/temp-holder.txt"
            if len(str(temp_file)) > 0:
                with open(temp_file, 'w') as f:
                    f.write('')
            exit(1)
            
        else:
            completion = client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": f"This is your identity and purpose {MODE_A}"},
                ]
            )

            bash_command = completion.choices[0].message.content.strip()
            match = re.search(r"```(?:bash)?\s*\n([^\n]+)", bash_command)
            new_command = match.group(1).strip()
            print(f"\nGenerated Bash Command:\n{new_command}")

            # 3. Confirm before executing
            confirm = input("\nDo you want to execute this command? (y/n)\n> ")

            if confirm.lower() == 'y':
                print("\nRunning command\n")
                output = subprocess.run([new_command], shell=True, text=True)

            else:
                print("Command canceled.")
            
    except ExceptionGroup as e:
        print(e)
