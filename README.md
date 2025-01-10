
```
movie-match
├─ .git
│  ├─ FETCH_HEAD
│  ├─ HEAD
│  ├─ config
│  ├─ description
│  ├─ hooks
│  │  ├─ applypatch-msg.sample
│  │  ├─ commit-msg.sample
│  │  ├─ fsmonitor-watchman.sample
│  │  ├─ post-update.sample
│  │  ├─ pre-applypatch.sample
│  │  ├─ pre-commit.sample
│  │  ├─ pre-merge-commit.sample
│  │  ├─ pre-push.sample
│  │  ├─ pre-rebase.sample
│  │  ├─ pre-receive.sample
│  │  ├─ prepare-commit-msg.sample
│  │  ├─ push-to-checkout.sample
│  │  └─ update.sample
│  ├─ index
│  ├─ info
│  │  └─ exclude
│  ├─ logs
│  │  ├─ HEAD
│  │  └─ refs
│  │     ├─ heads
│  │     │  └─ master
│  │     └─ remotes
│  │        └─ origin
│  │           └─ HEAD
│  ├─ objects
│  │  ├─ info
│  │  └─ pack
│  │     ├─ pack-9889e24bcfa325d99cf52cb6c0693205cb7444b2.idx
│  │     └─ pack-9889e24bcfa325d99cf52cb6c0693205cb7444b2.pack
│  ├─ packed-refs
│  └─ refs
│     ├─ heads
│     │  └─ master
│     ├─ remotes
│     │  └─ origin
│     │     └─ HEAD
│     └─ tags
├─ .gitignore
├─ adapter_services
│  ├─ omdb_adapter
│  │  ├─ .DS_Store
│  │  ├─ Dockerfile
│  │  ├─ app.py
│  │  ├─ controllers
│  │  │  └─ omdb_controller.py
│  │  ├─ requirements.txt
│  │  ├─ routes
│  │  │  └─ omdb_routes.py
│  │  └─ test
│  │     └─ test.py
│  ├─ streaming_availability_adapter
│  │  ├─ Dockerfile
│  │  ├─ app.py
│  │  ├─ controllers
│  │  │  └─ streaming_availability_controller.py
│  │  ├─ requirements.txt
│  │  ├─ routes
│  │  │  └─ streaming_availability_routes.py
│  │  └─ test
│  │     └─ test.py
│  └─ tmdb_adapter
│     ├─ Dockerfile
│     ├─ app.py
│     ├─ controllers
│     │  └─ tmdb_controller.py
│     ├─ requirements.txt
│     ├─ routes
│     │  └─ tmdb_routes.py
│     └─ test
│        └─ test.py
└─ docker-compose.yml

```