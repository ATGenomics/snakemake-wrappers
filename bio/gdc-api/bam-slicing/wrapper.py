__author__ = "David Lähnemann"
__copyright__ = "Copyright 2020, David Lähnemann"
__email__ = "david.laehnemann@uni-due.de"
__license__ = "MIT"

import os

log = snakemake.log_fmt_shell(stdout=True, stderr=True)

uuid = snakemake.params.get("uuid", "")
if uuid == "":
    raise ValueError("You need to provide a GDC UUID via the 'uuid' in 'params'.")

token_file = snakemake.params.get("gdc_token", "")
if token_file == "":
    raise ValueError(
        "You need to provide a GDC data access token file via the 'token' in 'params'."
    )
token = ""
with open(token_file) as tf:
    token = tf.read()
os.environ["CURL_HEADER_TOKEN"] = "'X-Auth-Token: {}'".format(token)

slices = snakemake.params.get("slices", "")
if slices == "":
    raise ValueError(
        "You need to provide 'region=chr1:1000-2000' or 'gencode=BRCA2' slice(s)  via the 'slices' in 'params'."
    )

extra = snakemake.params.get("extra", "")

os.system(
    f"curl --silent"
    f" --header $CURL_HEADER_TOKEN"
    f" 'https://api.gdc.cancer.gov/slicing/view/{uuid}?{slices}'"
    f" {extra}"
    f" --output {snakemake.output.bam} {log}"
)

if os.path.getsize(snakemake.output.bam) < 100000:
    with open(snakemake.output.bam) as f:
        if "error" in f.read():
            os.system(f"cat {snakemake.output.bam} {log}")
            raise RuntimeError(
                "Your GDC API request returned an error, check your log file for the error message."
            )
