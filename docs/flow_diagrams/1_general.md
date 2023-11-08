# What each process mean

## Request
Request (aka prayer request), is a simple text for what one would wish to pray
for

```mermaidjs
flowchart TB
A("/request") --> |User input request| B{Yes | Not Now}
B --> |Yes| C("What is prayer")
B --> |Not Now| D(( ))
C --> |User input request| E(( ))
```

## Prayer
Prayer, is a set of text you can attach to a request

## Answered
These texts are either:
1. imported from `Request`
1. a direct input from user as a simple text

In the case where a simple text is used, no prayers are added. If you would like
to have answered prayers added with a (set of) prayers, you should add them over
`Request` then import them over to `Answered`

## Delete
Delete allows you to remove any erroneous request, prayers or answered prayers.
This does NOT apply to prayers in answered. As this will affect the holistic
idea of answered prayers, prayers in answered prayers should not be deleted in
any use case


# APPENDIX

## Overall flow
```mermaidjs
flowchart TB
A(("/start")):::entryPoint -->|Hi Prayer Warrior! Welcome to the MVP bot! ...| B{ }

B --> B1("/request")
B --> B2("/pray")
B --> B3("/answered")

B --> BC["Display information about requests or prayers"]
BC --> C{ }
C --> C1("/listprayer")
C --> C2("/listall")
C --> C3("/listrequest")
C --> C1(/"listanswered")
```