FROM nginx:1-alpine

RUN apk add --no-cache gettext

COPY nginx.conf /etc/nginx/nginx.conf
COPY hash.js.template /etc/nginx/hash.js.template

CMD ["sh","-c","envsubst '${SERVER_NUM}' < /etc/nginx/hash.js.template > /etc/nginx/hash.js && exec nginx -g 'daemon off;'"]