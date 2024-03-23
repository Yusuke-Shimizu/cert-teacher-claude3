#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cert_teacher_claude3.cert_teacher_claude3_stack import CertTeacherClaude3Stack


app = cdk.App()
CertTeacherClaude3Stack(app, "CertTeacherClaude3Stack",
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
