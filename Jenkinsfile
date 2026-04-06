pipeline {
  agent none

  environment {
    GIT_NAME = "eea.climateadapt"
    GIT_ORG = "eea"
  }

  stages {
    stage('Release to Eggrepo') {
      when {
        allOf {
          environment name: 'CHANGE_ID', value: ''
          branch 'master'
        }
      }

      agent {
        label 'docker'
      }

      steps {
        withCredentials([
          [$class: 'UsernamePasswordMultiBinding', credentialsId: 'eea-jenkins', usernameVariable: 'EGGREPO_USERNAME', passwordVariable: 'EGGREPO_PASSWORD'],
          string(credentialsId: 'eea-jenkins-token', variable: 'GITHUB_TOKEN')
        ]) {
          sh '''
            docker run -i --rm --name="$BUILD_TAG-eggrelease" \
              -e GIT_BRANCH="$BRANCH_NAME" \
              -e GIT_NAME="$GIT_NAME" \
              -e GIT_ORG="$GIT_ORG" \
              -e GIT_TOKEN="$GITHUB_TOKEN" \
              -e EGGREPO_USERNAME="$EGGREPO_USERNAME" \
              -e EGGREPO_PASSWORD="$EGGREPO_PASSWORD" \
              eeacms/gitflow
          '''
        }
      }
    }
  }
}
