# Snap secrets on desktop environments

The [Secret Service](https://standards.freedesktop.org/secret-service/) is
used to manage secrets in traditional Linux desktop environments. This
service allows managing (add/delete/lock/etc) collections and
(add/delete/etc) items within collections. GNOME Keyring and KWallet
are the default Secret Service backends in GNOME and KDE environments, 
respectively.

The [password-manager-service](https://github.com/canonical/snapd/blob/master/interfaces/builtin/password_manager_service.go) 
interface can be used to grant snaps access to the Secret Service API.
However, access to this API is not mediated and grants access to all secrets
stored there (no per-snap restrictions can be enforced), making this solution
unsuitable for the confinement model. The position of the Security team has
been to reject auto-connection requests in most cases, limiting them to
manual connection and letting the user decide whether to connect to the
interface or not. 

The [Secret portal](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Secret.html) 
was designed as a secret storage solution for confined environments, such as
snaps. This portal allows applications to get a master secret that they can use
to encrypt their data. However, it requires a Secret portal backend to be
available on the host and a client that knows how to use it. The [desktop](https://github.com/canonical/snapd/blob/master/interfaces/builtin/desktop.go#L101)
interface grants snaps access to the Secret portal API.

Secret portal backend support was added to [GNOME Keyring](https://gitlab.gnome.org/GNOME/gnome-keyring/-/merge_requests/18)
and [KWallet](https://invent.kde.org/frameworks/kwallet/-/merge_requests/67)
and is available in their latest versions. Support for the Secret portal
was also added to [libsecret](https://gitlab.gnome.org/GNOME/libsecret/-/merge_requests/6)
and is available in their latest versions.


# Testing the Secret portal support

## Build and install the snap

```
$ snapcraft 
$ sudo snap install --dangerous secret-tool*.snap
```

## Create a password outside the snap and try to read it from the snap

Create the password using system secret-tool

```
$ secret-tool store --label='My password' origin system
Password: 1234
```

Read the password using system secret-tool

```
$ secret-tool lookup origin system
1234
```

Read the password using snap secret-tool

```
$ st lookup origin system
```

## Create a password inside the snap and try to read it from the system

Create the password using snap secret-tool

```
$ st store --label='My password' origin snap
Password: 1234
```

Read the password using snap secret-tool

```
$ st lookup origin snap
1234
```

Read the password using system secret-tool

```
$ secret-tool lookup origin snap
```

## Check per-snap encryption password was created successfully

Read the per-snap encryption password using system secret-tool

```
$ secret-tool lookup app_id snap.st
xxxxxxxxxxxxx
```