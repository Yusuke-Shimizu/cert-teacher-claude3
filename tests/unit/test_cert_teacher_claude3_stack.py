import aws_cdk as core
import aws_cdk.assertions as assertions

from cert_teacher_claude3.cert_teacher_claude3_stack import CertTeacherClaude3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in cert_teacher_claude3/cert_teacher_claude3_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CertTeacherClaude3Stack(app, "cert-teacher-claude3")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
