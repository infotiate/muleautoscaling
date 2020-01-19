sam package --template-file ./template.yaml \
    --output-template-file ./packaged.yaml \
    --s3-bucket $1
