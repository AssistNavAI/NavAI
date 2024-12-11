# AI Odyssey 2025 demo-project
<div align="center">
<img src="./VirtualAIOdysseyLogo.png" width="150" height="150">
</div>
<br/>

<b>`TODO` - COMPLETE SLIDES</b>
<br/><b>[AI Odyssey Demo Template](https://docs.google.com/presentation/d/1YTTtb9FceKOujMN4B6aGOnTijhrqfK9Tw75v7BQY5cA/edit?usp=sharing)</b>

## Demo Deployment Instructions

### Installing prerequisites

1. You need to provision a **RHOAI on OCP on AWS with NVIDIA GPUs** lab from **demo.redhat.com**
2. Once you have credentials, log in as cluster admin and start to provision **MinIO**
   1. Create a namespace to MinIO using: `oc new-project minio`
   2. Clone the following repo: `git clone https://github.com/tarcis-io/helm_minio.git`
   3. Change to repo directory: `cd helm_minio`
   4. Install MinIO via helm: `helm install helm-minio . -n minio`
   5. Wait until all pods are in _running_ state. Use the following command to check that: `oc get pods -w -n minio`
   6. To check the installation log in MinIO using **minio** as user and **minio123** as password
   7. Create a bucket called **navai**
   8. You're ready to go!

### GitOps

1. The **RHOAI on OCP on AWS with NVIDIA GPUs** lab provisions a GitOps instance. We'll use that!
   1. Log as the default admin user. Retrieve the password using the following instruction: `oc -n openshift-gitops get secret openshift-gitops-cluster -o jsonpath='{.data.admin\.password}' | base64 -d`
   2. Add this repo as a ArgoCD managed repo. You'll need to create personal access token inside gitlab in order to do that. Keep your token, you'll need to use that later!
      * Go to the 'Settings' menu and after that 'Repositories'
      * Use the following data:
        * Connection method: HTTPS
        * Name: navai
        * Project: default
        * Repository URL: https://gitlab.consulting.redhat.com/ai-odyssey-2025/neural-giants/demo-project.git
        * Username: Fill with your username
        * Password: Fill with your personal access token
        * Check 'Skip server verification'
      * Click on 'Connect'
      * Connection will be displayed in a list. You must see 'Connection Status' as **'Successful'**
2. We need to change some data in our artifacts first. Let's do that!
   1. data-connection-minio.yaml
      * Grab the API endpoint URL from MinIO using the following instruction: `echo "https://$(oc -n minio get route minio-api -o jsonpath='{.spec.host}')"`
      * Find the text **<MINIO_API_URL_HERE>** key with the output generated from the following commands:
        *   ```
            export MINIO_API_ENDPOINT=https://$(oc -n minio get route minio-api -o jsonpath='{.spec.host}') 
            yq -i '.stringData.AWS_S3_ENDPOINT = env(MINIO_API_ENDPOINT)' gitops/artifacts/data-connection-minio.yaml
            ```
      * Commit and push changes
3. Apply the following ArgoCD's application YAML
   * `oc apply -f gitops/navai-application.yaml`

### OpenShift AI

#### Workbench and development

1. Open OpenShift AI using the following route: `echo "https://$(oc -n redhat-ods-applications get route rhods-dashboard -o jsonpath='{.spec.host}')"`
2. Inside NavAI Data Science Project create a workbench with the following configuration:
   * Name: navai-workbench
   * Image selection: CUDA
   * Version selection: 2024.1
   * Container size: Small
   * Accelerator: NVIDIA GPU
   * Number of accelerators: 1
   * Check 'Create new persistent storage' and leave the name as 'navai-workbench'
   * Check 'Use a data connection' and check 'Use existing data connection'. Select 'minio' from dropdown list
3. Once your workbench is started, open it and clone this repo. Use your OpenShift credentials to log in. You can clone this repo using the UI or opening a terminal inside the workbench. Choose what is best for you. You'll need to use the same personal access token and username again.
   * Clone url: https://gitlab.consulting.redhat.com/ai-odyssey-2025/neural-giants/demo-project.git
4. Once this repo is cloned, open the **notebook/navai-yolov8.ipynb** file
5. Execute the steps in the presented order
6. **Skip step 2**
7. In **step 3**, change the **<S3_API_ENDPOINT_HERE>** key with the output generated from the following command: `echo "https://$(oc -n minio get route minio-api -o jsonpath='{.spec.host}')"`
8. Continue to execute the steps in the presented order until **step 6**. May some steps present some error messages. If that happen execute them again.
9. At the end of step 6 the expected outcome is having the **model uploaded to MinIO**

#### Deploy

1. At this point we already have our model exported to ONNX and uploaded to MinIO. It means that we're ready to go for deploy!
2. Open RHOAI and go to NavAI Data Science Project
3. Click on 'Models' tab
4. Choose 'Add model server' option
5. A modal window will be prompted. Fill the form with the data below:
   * Model server name: navai
   * Serving runtime: OpenVINO Model Server
   * Number of model server replicas to deploy: 1
   * Model server size: Small
   * Accelerator: NVIDIA GPU
   * Number of accelerators: 1
   * Check 'Make deployed models available through an external route'
   * Check 'Require token authentication'
   * Service account name: navai
6. At this point you'll have a model server with **one** token and **zero** deployed models. This is the expected outcome.
7. A 'Deploy model' button will be presented. Click on that.
8. A modal window will be prompted. Fill the form with the data below:
   * Model name: navai
   * Model framework (name - version): onnx - 1
   * Leave 'Existing data connection' checked. Here we will use the data connection done before.
     * Name: minio
     * Path: yolov8_navai_best.onnx
9. You will see a deployed model with Inference endpoint URI. Wait until 'Status' is in green check mode.
10. You're ready to infer the model. Let's test it!

#### Test

1. Go back to **navai-yolov8.ipynb** Jupyter notebook
2. Go to step 7
3. Change the **<NAVAI_INFERENCE_ENDPOINT_HERE>** key with the output generated from the following command: `echo "https://$(oc -n navai get route navai -o jsonpath='{.spec.host}')/v2/models/navai/infer"`
4. Change the **<NAVAI_TOKEN_SECRET_HERE>** key with the output generated from the following command: `oc -n navai get secret navai-navai-sa -o jsonpath='{.data.token}' | base64 -d`
5. Execute all the cells
6. All tests should pass!

### Run NavAI mobile local

**IMPORTANT:**

Due the limitations of time the mobile application can be ran only in local machine and we couldn't make it to take pictures. This is a WIP feature to next versions. Execute the following steps to run it locally.

1. Enter NavAI directory
```
cd navai-mobile
```
2. Install dependencies
```python
pip install --upgrade pip
pip install Flask opencv-python-headless requests gevent torch torchvision playsound
pip install tensorflow requests pillow matplotlib
```
3. Before we run NavAI Mobile we need first to do some changes so the app can infer the deployed model. Inside **navai-mobile/picture-taker.py** change:
   * Change the **<NAVAI_INFERENCE_ENDPOINT_HERE>** key with the output generated from the following command: `echo "https://$(oc -n navai get route navai -o jsonpath='{.spec.host}')/v2/models/navai/infer"`
   * Change the **<NAVAI_TOKEN_SECRET_HERE>** key with the output generated from the following command: `oc -n navai get secret navai-navai-sa -o jsonpath='{.data.token}' | base64 -d`
4. Let's make the magic happen!
```python
python3 picture-taker.py
```
5. If model detects a well-cover a beep will be made which means there is >90% chance of danger. Confidence score will be shown in **picture-taker.py logs**.

### Support docs
* https://stackoverflow.com/questions/15320267/package-opencv-was-not-found-in-the-pkg-config-search-path
* https://docs.opencv.org/4.x/d7/d9f/tutorial_linux_install.html
* https://www.redhat.com/en/blog/install-epel-linux
* https://medium.com/@albertqueralto/installing-opencv-within-docker-containers-for-computer-vision-and-development-a93b46996520
* https://docs.digitalearthafrica.org/en/latest/sandbox/notebooks/Beginners_guide/01_Jupyter_notebooks.html
* https://github.com/opendatahub-io/notebooks/tree/main
* https://docs.ultralytics.com/integrations/onnx/#summary
* https://github.com/opendatahub-io/odh-doc-examples/blob/main/storage/s3client_examples.ipynb

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.consulting.redhat.com/ai-odyssey-2025/neural-giants/demo-project.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.consulting.redhat.com/ai-odyssey-2025/neural-giants/demo-project/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
