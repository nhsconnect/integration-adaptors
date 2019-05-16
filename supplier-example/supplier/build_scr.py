import datetime

from scr.gp_summary_update import SummaryCareRecord
from utilities.message_utilities import MessageUtilities

HL7_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"


def build_scr(asid, patient_nhs_number, human_readable_payload):
    """Build a GP summary upload message

    :param asid: The ASID of this node.
    :param patient_nhs_number: The NHS number of the patient this record belongs to.
    :param human_readable_payload: The himan readable payload to be included in the summary message.
    :return: The GP summary message.
    """

    current_utc_time = datetime.datetime.utcnow()
    hl7_timestamp = current_utc_time.strftime(HL7_TIMESTAMP_FORMAT)

    gp_summary_properties = {
        "Id": MessageUtilities.get_uuid(),
        "creationTime": hl7_timestamp,
        "versionCode": "V3NPfIT4.2.00",
        "interactionId": {
            "root": "2.16.840.1.113883.2.1.3.2.4.12",
            "extension": "REPC_IN150016UK05"
        },
        "processingCode": {"code": "P"},
        "processingModeCode": {"code": "T"},
        "acceptAckCode": {
            "code": "NE"
        },
        "communicationFunctionRcv": {
            "device": {
                "id": {
                    "extension": "227319907548"
                }
            }
        },
        "communicationFunctionSnd": {
            "device": {
                "id": {
                    "extension": asid
                }
            }
        },
        "controlActEvent": {
            "classCode": "CACT",
            "moodCode": "EVN",
            "author1": {
                "agentSystemSDS": {
                    "id": {
                        "extension": asid
                    }
                }
            },
            "author": {
                "AgentPersonSDS": {
                    "id": {
                        "extension": "055888118514"
                    },
                    "agentPersonSDS": {
                        "id": {
                            "extension": "979603625513"
                        }
                    },
                    "part": {
                        "partSDSRole": {
                            "id": {
                                "extension": "R0260"
                            }
                        }
                    }
                }
            },
            "subject": {
                "GPSummary": {
                    "id": {
                        "root": MessageUtilities.get_uuid()
                    },
                    "effectiveTime": hl7_timestamp,
                    "author": {
                        "time": "20120315065138",
                        "AgentPersonSDS": {
                            "id": {
                                "extension": "055888118514"
                            },
                            "agentPersonSDS": {
                                "id": {
                                    "extension": "979603625513"
                                },
                                "name": "<family>NICA_Test_Automation_Healthchecks</family>"
                            }
                        }
                    },
                    "excerptForm": {
                        "CareDocs": {
                            "presentationText": {
                                "value": human_readable_payload,
                                "id": {"root": "EA3BCDEB-A439-4984-A519-2EE25EB3F24C"},
                                "effectiveTime": {"value": "200804161056"}
                            }
                        }
                    },
                    "recordTarget": {
                        "patient": {
                            "id": {
                                "extension": patient_nhs_number
                            }
                        }
                    }
                }
            }
        }
    }

    summary_care_record_builder = SummaryCareRecord()
    summary_care_record = summary_care_record_builder.populate_template(gp_summary_properties)
    return summary_care_record
