from langchain_core.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
import json
from datetime import datetime


import logging

logger = logging.getLogger(__name__)

'''
For the ease of this demo, we are emulating API integration into the following 3rd party tools.
1. Cisco Nexus Dashboard - Provides a REST API function that provides current and recommended firmware versions.
2. ITSM Tools ( Service Now - etc ) - Provides customer specific workflows, knowledge base lookups and change management schedules.
'''


def audit_firmware(devices: str) -> str:
    """ 
    Used as a placeholder for the visual layer of Studio
    Simulating the Nexus Dashboard API return to facilitate this demo.
    This is where you would build the API integration needed 
    """
    logger.info("Simulating firmware audit... returning static device list.")
    devicelist = {
        "devices": [
            {
                "hostname": "spine-sw01",
                "model": "N9K-C9336C-FX2",
                "role": "spine",
                "current_firmware": "7.0(3)I7(4)",
                "recommended_firmware": "10.4.5"
            },
            {
                "hostname": "spine-sw02",
                "model": "N9K-C9336C-FX2",
                "role": "spine",
                "current_firmware": "7.0(3)I7(4)",
                "recommended_firmware": "10.4.5"
            },
            {
                "hostname": "leaf-sw13",
                "model": "N9K-C93180YC-EX",
                "role": "leaf",
                "current_firmware": "9.2(1)",
                "recommended_firmware": "10.3.6"
            },
            {
                "hostname": "leaf-sw14",
                "model": "N9K-C93180YC-EX",
                "role": "leaf",
                "current_firmware": "9.2(1)",
                "recommended_firmware": "10.3.6"
            },
            {
                "hostname": "leaf-sw15",
                "model": "N9K-C93180YC-EX",
                "role": "leaf",
                "current_firmware": "9.2(1)",
                "recommended_firmware": "10.3.6"
            },
            {
                "hostname": "leaf-sw16",
                "model": "N9K-C93180YC-EX",
                "role": "leaf",
                "current_firmware": "9.2(1)",
                "recommended_firmware": "10.3.6"
            }
        ]
    }
    return json.dumps(devicelist)

# Pydantic models for input validation
class ITSMAuditInput(BaseModel):
    devices_json: str = Field(description="JSON string containing device information from firmware audit")

# Pydantic model for ITSMApproval input validation
class ITSMApprovalInput(BaseModel):
    plan: str = Field(description="The complete firmware upgrade plan to submit for approval")


def itsm_audit(devices_json: str) -> str:
    """ 
    Used as a placeholder for the visual layer of Studio
    Simulating the ITSM API return to facilitate this demo.
    itsm_changemanagement_items - Demonstrates Change Management Logic
    itsm_outage_items - Demonstrates Outage Observability Logic 
    itsm_knowledgebase_items - Demonstrates Knowledge Base Logic  
    """
    logger.info("Entering generate_upgrade_plan function with ITSM data retrieval.")
    logger.info(f"Received devices_json: {repr(devices_json)}")

    # Validate input
    if not devices_json or devices_json.strip() == "":
        error_msg = "Error: devices_json parameter is required and cannot be empty. Please pass the JSON output from FirmwareAudit tool."
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

    # Parse the input devices JSON
    try:
        if isinstance(devices_json, str):
            logger.info("Parsing devices_json string")
            devices_data = json.loads(devices_json)
        else:
            logger.info("devices_json is already a dictionary")
            devices_data = devices_json
    except json.JSONDecodeError as e:
        error_msg = f"Error: Failed to parse devices_json. Invalid JSON format: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
        
    # Validate that devices_data has the expected structure
    if not isinstance(devices_data, dict) or "devices" not in devices_data:
        error_msg = "Error: devices_json must contain a 'devices' key with device information"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
        
    # ITSM Change Management Items - devices that have scheduled maintenance
    itsm_changemanagement_items = {
        0: {
            "devicename": "leaf-sw14",
            "cr_number": "132145",
            "cr_status": "scheduled",
            "cr_description": "PowerSupply 1 Replacement - RMA"
        },
        1: {
            "devicename": "leaf-sw99",
            "cr_number": "651234",
            "cr_status": "scheduled",
            "cr_description": "QSFP Replacement - RMA"
        },
    }

    # ITSM Outage Items - devices currently experiencing issues
    itsm_outage_items = {
        0: {
            "incident_devicename": ["leaf-sw16"],
            "incident_number": "123456",
            "incident_status": "open",
            "incident_description": "Multiple TX errors observed on the port channel 115"
        },
        1: {
            "incident_devicename": ["server-sw99"],
            "incident_number": "654321",
            "incident_status": "open",
            "incident_description": "NVME is reporting errors"
        },
    }
    
    # ITSM Knowledge Base Items - relevant KB articles for device types
    itsm_knowledgebase_items = {
        0: {
            "kb_title": "Traffic egressing out same port-channel it is received on",
            "kb_number": "CSCve24947",
            "kb_device_type": "Cisco 9300 Series Switches",
            "kb_description": "The packet needs to have a destination mac (unicast packet) which is learned on the source port-channel. So if the packet came in port-channel1, then packet needs to have a dmac which is getting learned on po1.",
            "kb_notes": "This issue is solved in version 7.0(3)I4(7) and higher."
        },
        1: {
            "kb_title": "Cisco Nexus Spine Upgrades",
            "kb_number": "KB98765",
            "kb_device_type": "Cisco 9300 Series Spine Switches",
            "kb_description": "Cisco Nexus 9300 Spine Upgrades",
            "kb_notes": "All Cisco Spine Switches Upgrades should be approved by Jerry Garcia."
        },
    }
    
    # Combine all data into a single response
    combined_response = {
        "devices": devices_data,
        "itsm_changemanagement_items": itsm_changemanagement_items,
        "itsm_outage_items": itsm_outage_items,
        "itsm_knowledgebase_items": itsm_knowledgebase_items
    }
    
    result = json.dumps(combined_response, indent=2)
    logger.info("ITSM audit completed successfully")
    return result

def request_itsm_approval(plan: str) -> str:
    """Submit upgrade plan for ITSM approval."""
    logger.info("Submitting plan for ITSM approval...")
    
    if not plan or plan.strip() == "":
        error_msg = "Error: plan parameter is required and cannot be empty"
        logger.error(error_msg)
        return error_msg
    
    ticket_id = f"FWUP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    result = f"""ITSM Approval Status: SUBMITTED
    Ticket ID: {ticket_id}
    Submitted At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Plan Summary: {plan[:200]}{'...' if len(plan) > 200 else ''}

    Next Steps:
    1. Approval workflow initiated
    2. Technical review by network team
    3. Business impact assessment
    4. Final approval by change board"""
    
    logger.info(f"ITSM approval submitted successfully. Ticket: {ticket_id}")
    return result

# Tool definitions with clearer descriptions
firmware_audit_tool = Tool.from_function(
    func=audit_firmware,
    name="IntersightTool",
    description="Audit network devices to find those with outdated firmware. Call this first to get the device list. Returns JSON with device information including current and recommended firmware versions."
)

itsm_audit_tool = Tool.from_function(
    func=itsm_audit,
    name="ITSMAudit",
    description="Generate upgrade plan with ITSM integration data. MUST be called with the exact JSON output from FirmwareAudit as the devices_json parameter. Returns devices along with change management, outage, and knowledge base information.",
    args_schema=ITSMAuditInput
)

itsm_approval_tool = StructuredTool.from_function(
    func=request_itsm_approval,
    name="ITSMApproval",
    description="Submit the final upgrade plan for ITSM approval. Call this with the complete, structured upgrade plan that includes timing, priorities, and conflict analysis.",
    args_schema=ITSMApprovalInput
)

tools = [firmware_audit_tool, itsm_audit_tool, itsm_approval_tool]