#!/bin/bash
read file_path

pyats create testbed file --path "import/$file_path" --output testbed/device.yaml

