# Default Programs - Win32 apps | Microsoft Learn

Source: https://learn.microsoft.com/en-us/windows/win32/shell/default-programs
Retrieved: 2026-03-10

---

Use **Default Programs** to set the default user experience. Users can access **Default Programs** from Control Panel or directly from the **Start** menu. [Set Program Access and Computer Defaults (SPAD)](cpl-setprogramaccess), the primary defaults experience for users in Windows XP, is now one part of **Default Programs**.

> **Important**
> This topic does not apply for Windows 10. The way that default file associations work changed in Windows 10. For more information, see the section on **Changes to how Windows 10 handles default apps** in [this post](https://blogs.windows.com/windowsexperience/2015/05/20/announcing-windows-10-insider-preview-build-10122-for-pcs/).

When a user sets program defaults using **Default Programs**, the default setting applies only to that user and not to other users who might use the same computer. **Default Programs** provides a set of APIs (deprecated in Windows 8) that enable independent software vendors (ISVs) to include their programs or applications in the defaults system.

---

## Contents

- Introduction to Default Programs and Its Related API Set
- Registering an Application for Use with Default Programs
    - ProgIDs
    - Registration Subkey and Value Descriptions
    - RegisteredApplications
    - Full Registration Example
- Becoming the Default Browser
- Default Programs UI
- Best Practices for Using Default Programs
    - During Installation
    - After Installation
- Additional Resources
- Related topics

---

## Introduction to Default Programs and Its Related API Set

**Default Programs** is primarily designed for applications that use standard file types such as .mp3 or .jpg files or standard protocols, such as HTTP or mailto. Applications that use their own proprietary protocols and file associations do not typically use the **Default Programs** functionality.

After you register an application for **Default Programs** functionality, the following options and functionality are available via the API set:

- Restore all registered defaults for an application. *(Deprecated for Windows 8.)*
- Restore a single registered default for an application. *(Deprecated for Windows 8.)*
- Query for the owner of a specific default in a single call instead of searching the registry.
- Launch a UI for a specific application where a user can set individual defaults.
- Remove all per-user associations.

**Default Programs** also provides a UI that enables you to register an application in order to provide additional information to the user. For example, a digitally signed application can include a URL to the manufacturer's home page.

Use of the associated API set helps an application function correctly under User Account Control (UAC) introduced in Windows Vista. Under UAC, an administrator appears to the system as a standard user, so they cannot typically write to **HKEY_LOCAL_MACHINE**. Defaults must be registered on a per-user level, which prevents multiple users from overwriting each other's defaults.

---

## Registering an Application for Use with Default Programs

**Default Programs** requires each application to register explicitly the file associations, MIME associations, and protocols for which the application should be listed as a possible default.

### Registry structure overview

```
HKEY_LOCAL_MACHINE
   %ApplicationCapabilityPath%
      ApplicationDescription
      ApplicationName
      Hidden
      FileAssociations
         .file-extension1
         .file-extension2
         ...
      MIMEAssociations
         MIME
      Startmenu
         StartmenuInternet
         Mail
      UrlAssociations
         url-scheme
   SOFTWARE
      RegisteredApplications
         Unique Application Name = %ApplicationCapabilityPath%
```

### Example: Contoso WebBrowser

```
HKEY_LOCAL_MACHINE
   SOFTWARE
      Contoso
         WebBrowser
            Capabilities
               ApplicationDescription = This award-winning Contoso browser is better than ever. ...
               FileAssociations
                  .htm = ContosoHTML
                  .html = ContosoHTML
                  .shtml = ContosoHTML
                  .xht = ContosoHTML
                  .xhtml = ContosoHTML
               Startmenu
                  StartmenuInternet = Contoso.exe
               UrlAssociations
                  http = Contoso.Url.Http
                  https = Contoso.Url.Https
                  ftp = Contoso.Url.ftp
   SOFTWARE
      RegisteredApplications
         Contoso.WebBrowser.1.06 = SOFTWARE\Contoso\WebBrowser\Capabilities
```

### ProgIDs

An application must provide a specific ProgID. Be sure to include all the information that is typically written into the generic default subkey for the extension. Associations can be one-to-one or one-to-many (multiple extensions → one ProgID).

### Registration Subkey and Value Descriptions

#### Capabilities

| Value | Type | Meaning |
|---|---|---|
| ApplicationDescription | REG_SZ or REG_EXPAND_SZ | **Required.** Descriptive string about the application's capabilities. If not provided, the application does not appear in UI lists of potential default programs. |
| ApplicationName | REG_SZ or REG_EXPAND_SZ | **Optional.** The name shown in the Default Programs UI. If absent, the name of the executable is used. Must always match the name registered under RegisteredApplications. |
| Hidden | REG_DWORD | **Optional.** Set to 1 to suppress the application from the **Set your default programs** dialog. |

#### FileAssociations

Contains file associations claimed by the application — one value per extension, pointing to an application-specific ProgID.

#### MIMEAssociations

Contains MIME types claimed by the application. Value names must exactly match the MIME name in the MIME database. Each must be assigned an application-specific ProgID containing the corresponding CLSID.

#### Startmenu

Associated with the user-assignable **Internet** and **E-mail** entries in the Start menu. As of Windows 7, there are no longer **Internet** and **E-mail** entries in the Start menu; however, the **E-mail** data is still used for the default MAPI client.

#### UrlAssociations

Contains URL protocols claimed by the application. Each protocol must point to an application-specific ProgID. Different ProgIDs per protocol allow each to have its own execution string.

#### RegisteredApplications

```
HKEY_LOCAL_MACHINE\SOFTWARE\RegisteredApplications
```

Provides the OS with the registry location of the **Default Programs** information. The value name must match the application name.

### Full Registration Example: Litware Media Player

Application-specific ProgID for .mp3 MIME type:

```
HKEY_LOCAL_MACHINE
   SOFTWARE
      Classes
         LitwarePlayer11.MIME.MP3
            CLSID
               (Default) = {CD3AFA76-B84F-48F0-9393-7EDC34128127}
```

Application-specific ProgID for .mp3 file extension:

```
HKEY_LOCAL_MACHINE
   SOFTWARE
      Classes
         LitwarePlayer11.AssocFile.MP3
            (Default) = MP3 Format Sound
            DefaultIcon
               (Default) = %ProgramFiles%\Litware\litware.dll, 0
            shell
               open
                  command
                     (Default) = %ProgramFiles%\Litware\litware.exe
```

Combined ProgID for .mpeg MIME type and file extension:

```
HKEY_LOCAL_MACHINE
   SOFTWARE
      Classes
         LitwarePlayer11.AssocFile.MPG
            (Default) = Movie Clip
            CLSID
               (Default) = {D92B76F4-CFA0-4b93-866B-7730FEB4CD7B}
            DefaultIcon
               (Default) = %ProgramFiles%\Litware\litware.dll, 0
            shell
               open
                  command
                     (Default) = %ProgramFiles%\Litware\litware.exe
```

Default Programs registration using the ProgIDs above:

```
HKEY_LOCAL_MACHINE
   SOFTWARE
      Litware
         LitwarePlayer
            Capabilities
               ApplicationDescription = The new Litware Media Player breaks new ground in exciting fictional programs.
               FileAssociations
                  .mp3 = LitwarePlayer11.AssocFile.MP3
                  .mpeg = LitwarePlayer11.AssocFile.MPG
               MimeAssociations
                  audio/mp3 = LitwarePlayer11.MIME.MP3
                  audio/mpeg = LitwarePlayer11.AssocFile.MPG
```

Location registration:

```
HKEY_LOCAL_MACHINE
   SOFTWARE
      RegisteredApplications
         Litware Player = Software\Litware\LitwarePlayer\Capabilities
```

---

## Becoming the Default Browser

Browser registration must follow the best practices outlined in this topic. Windows can present a system notification through which the user can select the browser as the system default. This notification is shown when:

- The browser's installer calls `SHChangeNotify` with the `SHCNE_ASSOCCHANGED` flag.
- Windows detects that one or more new applications have registered to handle both `http://` and `https://` protocols, and the user has not yet been notified.

Recommended installer code after writing registry keys:

```c
void NotifySystemOfNewRegistration()
{
    SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_DWORD | SHCNF_FLUSH, nullptr, nullptr);
    Sleep(1000);
}
```

---

## Default Programs UI

The **Default Programs** item in Control Panel shows:

- **Set your default programs** — A list of all registered programs. The user can assign all defaults to one program, or click **Choose defaults for this program** to open the **Set associations for a program** window for granular control.
- Applications can call `IApplicationAssociationRegistrationUI::LaunchAdvancedAssociationUI` to open this window directly.

---

## Best Practices for Using Default Programs

### During Installation

In addition to standard XP-era installation procedures, a Vista+ application must register with **Default Programs**.

Sequence:
1. Install necessary binary files.
2. Write ProgIDs to `HKEY_LOCAL_MACHINE`. Create **application-specific** ProgIDs for associations.
3. Register with **Default Programs** as described above.

### After Installation — First Run Experiences

When the application is first run by a user, present UI with two choices:

1. **Accept the default application settings** (selected by default).
2. **Customize the default application settings.**

Prior to Windows 8:
- If the user accepts: call `IApplicationAssociationRegistration::SetAppAsDefaultAll`.
- If the user customizes: call `IApplicationAssociationRegistrationUI::LaunchAdvancedAssociationUI`.

### Set an Application to Check Whether It Is the Default

> **Note**: Not supported as of Windows 8.

Call `IApplicationAssociationRegistration::QueryAppIsDefault` or `QueryAppIsDefaultAll` to check default status. If not default, present UI asking whether to make it the default — always include a "don't ask again" checkbox. **Never reclaim a default without asking the user.**
