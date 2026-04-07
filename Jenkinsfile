pipeline {
  agent any

  environment {
    GIT_NAME = "eea.climateadapt.plone"
    GIT_ORG = "eea"
    SONARQUBE_TAGS = "climate-adapt.eea.europa.eu,next-climate-adapt.eea.europa.eu,climate-adapt.europa.eu"
  }

  stages {
    stage('Cosmetics') {
      steps {
        parallel(
          /*
          "JS Hint": {
            node(label: 'docker') {
              script {
                sh '''docker run -i --rm --name="$BUILD_TAG-jshint" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/jshint'''
              }
            }
          },

          "CSS Lint": {
            node(label: 'docker') {
              script {
                sh '''docker run -i --rm --name="$BUILD_TAG-csslint" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/csslint'''
              }
            }
          },
          */

          "Ruff": {
            node(label: 'docker') {
              script {
                if (!(env.BRANCH_NAME != "master" && (env.CHANGE_ID == null || env.CHANGE_ID == ''))) {
                  return
                }
                checkout scm
                fix_result = sh(script: '''docker run --pull=always --name="$BUILD_TAG-ruff-fix" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/ruff format''', returnStatus: true)
                sh '''docker cp $BUILD_TAG-ruff-fix:/code/$GIT_NAME .'''
                sh '''cp -rf $GIT_NAME/* .'''
                sh '''rm -rf $GIT_NAME'''
                sh '''docker rm -v $BUILD_TAG-ruff-fix'''
                FOUND_FIX = sh(script: '''git diff --name-only '*.py' | wc -l''', returnStdout: true).trim()

                if (FOUND_FIX != '0') {
                  withCredentials([string(credentialsId: 'eea-jenkins-token', variable: 'GITHUB_TOKEN')]) {
                    sh '''sed -i "s|url = .*|url = https://eea-jenkins:$GITHUB_TOKEN@github.com/eea/$GIT_NAME.git|" .git/config'''
                  }
                  sh '''git fetch origin $GIT_BRANCH:$GIT_BRANCH'''
                  sh '''git checkout $GIT_BRANCH'''
                  sh '''git add -- '*.py' '''
                  sh '''git commit -m "style: Automated code fix" '''
                  sh '''git push --set-upstream origin $GIT_BRANCH'''
                  sh '''exit 1'''
                }
              }
            }
          }
        )
      }
    }

    stage('Code') {
      steps {
        parallel(
          "ZPT Lint": {
            node(label: 'docker') {
              sh '''docker run -i --rm --name="$BUILD_TAG-zptlint" -e GIT_BRANCH="$BRANCH_NAME" -e ADDONS="$GIT_NAME" -e DEVELOP="src/$GIT_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/plone-test:4 zptlint'''
            }
          },

          /*
          "JS Lint": {
            node(label: 'docker') {
              sh '''docker run -i --rm --name="$BUILD_TAG-jslint" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/jslint4java'''
            }
          },
          */

          "Ruff": {
            node(label: 'docker') {
              script {
                if (!(env.BRANCH_NAME != "master" && (env.CHANGE_ID == null || env.CHANGE_ID == ''))) {
                  return
                }
                checkout scm
                fix_result = sh(script: '''docker run --pull=always --name="$BUILD_TAG-ruff-fix" -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/ruff check''', returnStatus: true)
                sh '''docker cp $BUILD_TAG-ruff-fix:/code/$GIT_NAME .'''
                sh '''cp -rf $GIT_NAME/* .'''
                sh '''rm -rf $GIT_NAME'''
                sh '''docker rm -v $BUILD_TAG-ruff-fix'''
                FOUND_FIX = sh(script: '''git diff --name-only '*.py' | wc -l''', returnStdout: true).trim()

                if (FOUND_FIX != '0') {
                  withCredentials([string(credentialsId: 'eea-jenkins-token', variable: 'GITHUB_TOKEN')]) {
                    sh '''sed -i "s|url = .*|url = https://eea-jenkins:$GITHUB_TOKEN@github.com/eea/$GIT_NAME.git|" .git/config'''
                  }
                  sh '''git fetch origin $GIT_BRANCH:$GIT_BRANCH'''
                  sh '''git checkout $GIT_BRANCH'''
                  sh '''git add -- '*.py' '''
                  sh '''git commit -m "lint: Automated code fix" '''
                  sh '''git push --set-upstream origin $GIT_BRANCH'''
                  sh '''exit 1'''
                }
              }
            }
          },

          "i18n": {
            node(label: 'docker') {
              sh '''docker run -i --rm --name=$BUILD_TAG-i18n -e GIT_SRC="https://github.com/eea/$GIT_NAME.git" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/i18ndude'''
            }
          }
        )
      }
    }

    stage('Tests') {
      steps {
        parallel(
          "Plone6 & Python3": {
            node(label: 'docker') {
              sh '''docker run --pull="always" -i --name="$BUILD_TAG-tests" -e GIT_NAME="$GIT_NAME" -e GIT_BRANCH="$BRANCH_NAME" -e DEVELOP="src/$GIT_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" eeacms/plone-test:6'''
              sh '''docker cp $BUILD_TAG-tests:/app/coverage ./coverage'''
              sh '''docker rm -v $BUILD_TAG-tests'''
              stash includes: 'coverage/**', name: 'coverage'
            }
          }
        )
      }
    }

    stage('Report to SonarQube') {
      when {
        allOf {
          environment name: 'CHANGE_ID', value: ''
        }
      }
      steps {
        node(label: 'swarm') {
          script {
            checkout scm
            unstash 'coverage'
            junit 'coverage/junit-results/testreports/*.xml'
            def scannerHome = tool 'SonarQubeScanner'
            def nodeJS = tool 'NodeJS11'
            sh "sed -i 's|<source>/app</source>|<source>.</source>|g' coverage/coverage.xml"
            sh "sed -i \"s|filename=\\\"src/$GIT_NAME/|filename=\\\"|g\" coverage/coverage.xml"
            sh "sed -i \"s|package name=\\\"src\\.$GIT_NAME|package name=\\\"|g\" coverage/coverage.xml"
            withSonarQubeEnv('Sonarqube') {
              sh "export PATH=$PATH:${scannerHome}/bin:${nodeJS}/bin; sonar-scanner -Dsonar.python.xunit.skipDetails=true -Dsonar.python.xunit.reportPath=coverage/junit-results/testreports/*.xml -Dsonar.python.coverage.reportPaths=coverage/coverage.xml -Dsonar.sources=./eea -Dsonar.exclusions=**/tests/**,**/setup.py -Dsonar.projectKey=$GIT_NAME-$BRANCH_NAME -Dsonar.projectVersion=$BRANCH_NAME-$BUILD_NUMBER"
              sh '''try=2; while [ $try -gt 0 ]; do curl -s -XPOST -u "${SONAR_AUTH_TOKEN}:" "${SONAR_HOST_URL}api/project_tags/set?project=${GIT_NAME}-${BRANCH_NAME}&tags=${SONARQUBE_TAGS},${BRANCH_NAME}" > set_tags_result; if [ $(grep -ic error set_tags_result ) -eq 0 ]; then try=0; else cat set_tags_result; echo "... Will retry"; sleep 60; try=$(( $try - 1 )); fi; done'''
            }
          }
        }
      }
    }

    stage('Pull Request') {
      when {
        not {
          environment name: 'CHANGE_ID', value: ''
        }
        environment name: 'CHANGE_TARGET', value: 'master'
      }
      steps {
        node(label: 'docker') {
          script {
            if (env.CHANGE_BRANCH != "develop" && !(env.CHANGE_BRANCH.startsWith("hotfix"))) {
              error "Pipeline aborted due to PR not made from develop or hotfix branch"
            }
            withCredentials([string(credentialsId: 'eea-jenkins-token', variable: 'GITHUB_TOKEN')]) {
              sh '''docker run -i --rm --name="$BUILD_TAG-gitflow-pr" -e GIT_CHANGE_BRANCH="$CHANGE_BRANCH" -e GIT_CHANGE_AUTHOR="$CHANGE_AUTHOR" -e GIT_CHANGE_TITLE="$CHANGE_TITLE" -e GIT_TOKEN="$GITHUB_TOKEN" -e GIT_BRANCH="$BRANCH_NAME" -e GIT_CHANGE_ID="$CHANGE_ID" -e GIT_ORG="$GIT_ORG" -e GIT_NAME="$GIT_NAME" eeacms/gitflow'''
            }
          }
        }
      }
    }

    stage('Release') {
      when {
        allOf {
          environment name: 'CHANGE_ID', value: ''
          branch 'master'
        }
      }
      steps {
        node(label: 'docker') {
          withCredentials([
            [$class: 'UsernamePasswordMultiBinding', credentialsId: 'eea-jenkins', usernameVariable: 'EGGREPO_USERNAME', passwordVariable: 'EGGREPO_PASSWORD'],
            string(credentialsId: 'eea-jenkins-token', variable: 'GITHUB_TOKEN'),
            [$class: 'UsernamePasswordMultiBinding', credentialsId: 'pypi-jenkins', usernameVariable: 'PYPI_USERNAME', passwordVariable: 'PYPI_PASSWORD']
          ]) {
            sh '''docker run -i --rm --name="$BUILD_TAG-gitflow-master" -e GIT_BRANCH="$BRANCH_NAME" -e EGGREPO_USERNAME="$EGGREPO_USERNAME" -e EGGREPO_PASSWORD="$EGGREPO_PASSWORD" -e GIT_NAME="$GIT_NAME" -e PYPI_USERNAME="$PYPI_USERNAME" -e PYPI_PASSWORD="$PYPI_PASSWORD" -e GIT_ORG="$GIT_ORG" -e GIT_TOKEN="$GITHUB_TOKEN" eeacms/gitflow'''
          }
        }
      }
    }
  }

  post {
    changed {
      script {
        def url = "${env.BUILD_URL}/display/redirect"
        def status = currentBuild.currentResult
        def subject = "${status}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
        def details = """<h1>${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${status}</h1>
                         <p>Check console output at <a href="${url}">${env.JOB_BASE_NAME} - #${env.BUILD_NUMBER}</a></p>
                      """

        emailext(subject: '$DEFAULT_SUBJECT', to: '$DEFAULT_RECIPIENTS', body: details)
      }
    }
  }
}
