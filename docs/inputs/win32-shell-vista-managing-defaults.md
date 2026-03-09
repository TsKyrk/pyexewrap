# Managing Default Applications - Win32 apps | Microsoft Learn

Source: https://learn.microsoft.com/en-us/windows/win32/shell/vista-managing-defaults
Retrieved: 2026-03-10

---

The **Set Program Access and Computer Defaults** (SPAD) feature was added to Windows XP and later versions of Windows to manage per-computer defaults. In addition to SPAD, Windows Vista introduced the concept of per-user default applications and the **Default Programs** item in Control Panel.

> **Important**
> This topic does not apply for Windows 10. The way that default file associations work changed in Windows 10. For more information, see the section on **Changes to how Windows 10 handles default apps** in [this post](https://blogs.windows.com/windows-insider/2015/05/20/announcing-windows-10-insider-preview-build-10122-for-pcs/).

Per-user default settings are specific to an individual user account on the system. If per-user default settings are present, they take precedence over corresponding per-computer defaults for that account. As of Windows 8, the extensibility system for file type and protocol defaults is strictly per-user and per-computer defaults are ignored. SPAD also changed in Windows 8 to set per-user defaults.

- On systems running versions of Windows earlier than Windows 8, a newly created user account receives per-computer defaults until per-user defaults are established. In Windows Vista and later, users can use the **Default Programs** item in Control Panel to set or change their per-user defaults. In addition, when an application is run for the first time, per-user defaults can be set using the guidelines that follow in the Application First Run and Defaults section.
- On systems running Windows 8, a newly created user account relies on per-user defaults from the start and the setting of those defaults on first run as explained in the Application First Run and Defaults section is no longer supported.

An application must register with both SPAD and the Default Programs feature to be offered as the default program in Windows Vista and later.

---

## Contents

- Default Programs Item in Control Panel
- Set Program Access and Computer Defaults
    - Setting Defaults in SPAD
    - Hide Access in SPAD
- Registering for Application Entry Points
    - Open With
    - Start Menu and Quick Launch Bar
- Application Installation and Defaults
- Application Upgrades and Defaults
- Application First Run and Defaults
- Verifying Defaults and Asking for User Consent
- Application Compatibility Tips
- Additional Resources
- Related topics

---

## Default Programs Item in Control Panel

**Default Programs** is a feature introduced in Windows Vista, accessible directly from the **Start** menu as well as Control Panel. It provides a new infrastructure that works with standard user privilege (not elevated) and is designed to enable users and applications to manage per-user defaults. For users, Default Programs provides a unified and easily accessible way to manage defaults, file associations, and Autoplay settings across all applications on the system. For applications, using the per-user scope provided by the Default Programs APIs offers the following advantages:

- **No Elevation** — An application does not have to elevate its privileges to claim defaults.
- **Good Citizenship** — On a multiple-user computer, each user can select different default applications.
- **Default Management** — Default Programs APIs offer a reliable and consistent mechanism for self-checking the default status and reclaiming lost settings without resorting to writing directly to the registry. However, as of Windows 8, we do not recommend that applications query the default status because an application can no longer change the default settings — those changes can be made only by the user.

To enable your application to manage defaults effectively, you must register your application as a potential default program. For details on registering and using the Default Programs APIs, see [Default Programs](default-programs).

Default Programs also provides these two features:

- **Reusable Defaults UI** — The UI of both the program defaults (**Set your default programs**) and file associations (**Associate a file type or protocol with a program**) can be reused and called from within an application.
- **Inclusion of URL and Marketing Information** — As part of the **Set your default programs** page, an application can provide marketing information and a link to the vendor's website, derived from the Authenticode certificate.

## Set Program Access and Computer Defaults

**Set Program Access and Computer Defaults** (SPAD) enables administrators to manage computer-wide defaults that are inherited by all new users of that computer. As of Windows 8, SPAD affects only user-specific defaults.

For more information on registering an application in SPAD, see [Working with Set Program Access and Computer Defaults (SPAD)](cpl-setprogramaccess) and [Registering Programs with Client Types](reg-middleware-apps).

### Setting Defaults in SPAD

Per-user defaults override per-computer defaults.

- **Before Windows 8**: Defaults set in SPAD (per-computer) will not be seen by users if corresponding per-user defaults are set. New user accounts on a computer initially inherit the computer defaults. The first time a user runs an application, the application should prompt the user to assign their per-user defaults.
- **As of Windows 8**: All defaults are per-user and any per-computer default setting is ignored. Applications can no longer set default choices programmatically.

When a Windows 8 application implements **Set as Default** in SPAD, they must register their file types and protocols in Default Programs, using the same application name used in SPAD.

### Hide Access in SPAD

The hide access option removes all entry points to the appropriate applications:

- Desktop
- Start menu
- Quick Launch bar (Windows Vista and earlier only)
- Notification area
- Shortcut menus
- Folder task band

### Alternate Hide Access Method in SPAD

For legacy applications where full Hide Access implementation is not practical, an alternative is to uninstall the application. Sample C++ code (using `ShellExecute` to open `appwiz.cpl`) is provided in the original documentation.

## Registering for Application Entry Points

An application can have many entry points within the operating system:

- Desktop
- Start menu
- Quick Launch bar (Windows Vista and earlier only)
- Notification area
- Shortcut menus
- Folder task band

### Open With

The **Open With** shortcut menu enables the user to select an application that can handle a specific file type. An application should always register for **Open With** so users are presented with it as a choice. Applications can register both file types and protocols for **Open With**.

For information on registering for **Open With**, see [Introduction to File Associations](fa-intro).

### Start Menu and Quick Launch Bar

In Windows Vista and later, an application creates a shortcut in `%ProgramData%\Microsoft\Windows\Start Menu\Programs` to appear in the Start menu for all users.

> **Note**: The Quick Launch bar is no longer available as of Windows 7. The alternative is to have the application pinned to the Taskbar, but pinning cannot be done programmatically — it is strictly a user choice.

## Application Installation and Defaults

During installation, an application should:
- Copy its binaries to the hard disk
- Write its ProgIDs to the registry
- Register for Default Programs and **Open With** for every file association it is a candidate to handle

Applications should not set per-user defaults during installation (the installer may not be the intended user). As of Windows 8, per-computer defaults are not supported and applications cannot change per-user default settings.

## Application Upgrades and Defaults

Upgrade procedures should not change the state of per-user defaults. However, it is acceptable to check computer-level file associations and repair them if they have been corrupted.

## Application First Run and Defaults

> **Note**: As of Windows 8, the system handles this on behalf of all applications. Applications themselves can no longer query and change defaults — only the user can. Applications can provide an entry point to Default Programs in Control Panel by calling `IApplicationAssociationRegistrationUI::LaunchAdvancedAssociationUI`.

The guideline for establishing per-user defaults (pre-Windows 8): When an application is first run for a specific user, it should request user preferences for defaults and file associations.

The recommended UI should provide two clear choices:
1. **Accept all defaults** that the application would like to claim.
2. **Customize** by accepting or not accepting default selections and program settings individually.

## Verifying Defaults and Asking for User Consent

> **Note**: Not supported as of Windows 8.

After registering with Default Programs, the `IApplicationAssociationRegistration` interface provides methods to check whether an application is the current default.

Any application that wants to claim defaults must first ask the user. The user should be asked whether they want to make the application the default or leave the current default in place. There should also be an option not to be asked again.

## Application Compatibility Tips

### Avoid Triggering Per-User Virtualization

Applications should always run with only standard user rights. With UAC, blocked attempts to write to protected registry areas or system files are "virtualized" by an AppCompat layer — but applications should not rely on this as a long-term solution.

### Avoid AppCompat Warnings or Blocks from the Program Compatibility Assistant

The Program Compatibility Assistant (PCA), introduced in Windows Vista, monitors programs for known issues and notifies users if problems are detected. ISVs should use available tools to ensure compatibility with Windows Vista and later.

### Support for Previous Windows Operating System Versions

The Default Programs infrastructure is not available before Windows Vista. Applications should retain their older application-defaults code for compatibility with older versions of Windows, and run an OS version check at installation to determine which code path to follow.

To support upgrades from Windows XP to Windows Vista or later: add all registry entries required for Default Programs even when installing on Windows XP. The registration will have no effect on XP, but will be ready if the computer is later upgraded.
