# How File Associations Work - Win32 apps | Microsoft Learn

Source: https://learn.microsoft.com/en-us/windows/win32/shell/fa-how-work
Retrieved: 2026-03-10

---

File associations define how the Shell treats a file type on the system.

This topic is organized as follows:

- About File Associations
- When You Should Implement or Modify File Associations
- How File Associations Work
- Additional Resources
- Related topics

## About File Associations

File associations control the following functionality:

- Which application launches when a user double-clicks a file.
- Which icon appears for a file by default.
- How the file type appears when viewed in Windows Explorer.
- Which commands appear in a file's shortcut menu.
- Other UI features, such as tooltips, tile info, and the details pane.

Application developers can use file associations to control how the Shell treats custom file types, or to associate an application with existing file types. For example, when an application is installed, the application can check for the presence of existing file associations, and either create or override those file associations.

Users can control some aspects of file associations to customize how the Shell treats a file type either by using the **Open With** UI, or editing the registry.

In the Windows Explorer window shown in the screen shot below, the Shell displays different icons for each file, based on the icon associated with the file type. If the user double-clicks the file **Sample Bitmap Image**, the Shell launches Paint and uses it to open the file because on this system, Paint is associated with .bmp files. People can control these actions using file associations.

## When You Should Implement or Modify File Associations

Applications can use files for various purposes: some files are used exclusively by the application, and are not typically accessed by users, while other files are created by the user and are often opened, searched for, and viewed from the Shell.

Unless your custom file type is used exclusively by the application, you should implement file associations for it. As a general rule, implement file associations for your custom file type if you expect the user to interact directly with these files in any way. That includes using the Shell to browse and open the files, searching the content or properties of the files, and previewing the files.

If your application is handling an existing file type, do not modify the file association unless you want to modify the way the Shell handles all files of this type.

## How File Associations Work

Files are exposed in the Shell as Shell items. To control file associations, application developers can register a mapping between the file type and the handlers (COM objects that provide functionality for the file type's Shell items). When the Shell needs to query for the file associations of a file type, it creates an array of registry keys containing the associations for the file type, and checks these keys for the appropriate file associations to use.
