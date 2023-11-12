FROM node:18-slim as build

WORKDIR /usr/src/

RUN apt-get update && apt-get install -y git
RUN git clone --depth 1 https://github.com/medplum/medplum.git
RUN cd medplum && npm ci && npm run build -- --filter=@medplum/app

WORKDIR /usr/src/medplum/packages/app

ENTRYPOINT [ "npm", "run", "dev", "--", "--host"]