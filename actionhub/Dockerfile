FROM node:20.16-alpine

RUN mkdir -p /code
WORKDIR /code

COPY . /code

ENV ACTION_HUB_BASE_URL=https://actionhubimage-536370090817.europe-west4.run.app
ENV ACTION_HUB_LABEL=TestHub
ENV ACTION_HUB_SECRET=abcdefg123456789

RUN yarn install --production && yarn cache clean
RUN yarn build

CMD ["yarn","start"]

EXPOSE 8080
