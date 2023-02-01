This is a fork of the official OpenTrons git repo focused on making the last version of the OpenTrons app with support for the OT1 buildable and usable on modern systems.

If you just want the binary, which has been tested only on Xubuntu 20.04, then go to the Releases page and get `opentrons-ot1-app.tar.gz`, extract it and run `./ot-app`. You can also try the 

Note that this is all based on the very last commit related to the 2.5.x OpenTrons app, which as far is the last software to support the OpenTrons OT-1.

The last official release of the OT-1 app and python module were version 2.5.2 but there is no tagged release for 2.5.2 in the official OpenTrons git repo. The closest is 2.5.0 which is from August 15 2017. The files in the official 2.5.2 `.deb` file are from August 18 2017. The 2.5.0 tag was on the branch called `ot1-stable` and commits continued on this branch until Jan 24 2018. I have made this branch the default branch on this repo and the instructions and released binaries are all from this last commit so they should be more recent than the 2.5.2 release.

The original `README.md` is included as `README.md.orig`. The official 2.5.2 release would likely work on Ubuntu 17.10 or 17.04 based on the release dates, but building the original codebase using the original instructions would still fail due to insufficiently constrained dependencies. This has been fixed here and it should now build on modern systems.

# Building

As of this writing (Jan 31st 2023) these build instructions work on Xubuntu 20.04 but who knows if all of the necessary dependencies will continue to be available in the future. For this reason, I have checked in all of `api/python_virtualenv` and all of `app/node_modules` except `app/node_modules/electron/dist/electron` which was too large for github to accept. That file is included in the `binaries.tar.gz` in Releases.

The binaries for the relevant versions of python, pip, nvm and node are included as part of a Release as the `tools.tar.gz` file and there I have also included everything that landed in my `~/.cache/` directory as the `cache.tar.gz`.

If downloads of e.g. electron related stuff fails then you might want to extract the contents of `cache.tar.gz` in your `~/.cache/` directory before following these instructions (make sure it doesn't land in `/.cache/cache/`).


The following instructions were tested using Python 3.8.10, pip version 22.3.1 and python virtualenv version 20.17.1.

The `api/dist/opentrons-api-server` binary is included in this git repo. If you want to re-build it, first do:

```
rm -rf api/dist/*
```

If you don't want to rebuild this part, skip to the "Building the app" section.

## Building the API server

Enter the api dir:

```
cd api/
```

If you don't want to re-download all of the python dependencies (they have been checked into this git repo) then you can skip this step:

```
rm -rf python_virtualenv
virtualenv python_virtualenv
make install
```

Compile the API server:

```
make exe
```

You can test if it starts without errors by running:

```
./dist/opentrons-api-server
```

## Building the app

Now to build the electron app move to the `app/` dir:

```
cd ../app
```

First install the recommended node version using nvm (node version manager):

```
nvm install 7.10.1
```

or if it's already installed then:

```
nvm use 7.10.1
```

then:

```
make install
```

You will then need a different node version to build the electron app:

```
nvm install 10.19.0
```

or if it's already installed then:

```
nvm use 10.19.0
```

Then:

```
make build package
```

Finally, to run the app:

```
cd dist/linux-unpacked
./ot-app
```

