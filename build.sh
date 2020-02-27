set -e

./cards.py
./setup-build.py

rm -rf dist
mkdir dist
mkdir dist/twitch


( cd config && yarn install --pure-lockfile && yarn build )
( cd overlay && yarn install --pure-lockfile && yarn build )
( cd mobile && yarn install --pure-lockfile && yarn build )
( cd client && yarn install --pure-lockfile && yarn build )

mv config/dist dist/twitch/config
mv overlay/dist dist/twitch/overlay
mv mobile/dist dist/twitch/mobile

( cd dist/twitch && zip -r ../twitch.zip * )
cp client/build/deckmaster-* dist
