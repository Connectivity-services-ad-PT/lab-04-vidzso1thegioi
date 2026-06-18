from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

app = FastAPI(
    title="Analytics Integrated Service",
    version="0.4.0",
    description="FIT4110 Lab04 Analytics service packaged with Docker"
)


def problem_details(status: int, title: str, detail: str, instance: str):
    return {
        "type": "https://smart-campus.local/problems/error",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "status" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details(
            exc.status_code,
            "HTTP error",
            str(exc.detail),
            str(request.url.path)
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=problem_details(
            422,
            "Invalid request",
            "Request validation failed",
            str(request.url.path)
        )
    )


def require_auth(authorization: Optional[str], instance: str):
    if authorization != "Bearer lab-token":
        raise HTTPException(
            status_code=401,
            detail=problem_details(
                401,
                "Unauthorized",
                "Missing or invalid bearer token",
                instance
            )
        )


telemetry_items = [
    {
        "eventId": "d6703cc8-9e79-415d-ac03-a4dc7f6ab43c",
        "eventType": "telemetry.ingested",
        "timestamp": "2019-08-24T14:15:22Z",
        "source": "iot",
        "data": {
            "deviceId": "SENSOR-001",
            "sensorType": "temperature",
            "value": 38.5,
            "unit": "celsius",
            "timestamp": "2019-08-24T14:15:22Z",
            "zoneId": "ZONE-A"
        }
    }
]

camera_motion_items = [
    {
        "eventId": "c6703cc8-9e79-415d-ac03-a4dc7f6ab43c",
        "correlationId": "48fb4cd3-2ef6-4479-bea1-7c92721b988c",
        "eventType": "camera.motion.detected",
        "timestamp": "2019-08-24T14:15:22Z",
        "source": "camera",
        "data": {
            "cameraId": "CAM-001",
            "zoneId": "ZONE-A",
            "confidence": 0.91
        }
    }
]

policy_decision_items = [
    {
        "eventId": "p6703cc8-9e79-415d-ac03-a4dc7f6ab43c",
        "eventType": "policy.decision.created",
        "timestamp": "2019-08-24T14:15:22Z",
        "source": "core-business",
        "data": {
            "policyId": "POLICY-001",
            "decision": "allow",
            "zoneId": "ZONE-A"
        }
    }
]

access_log_items = [
    {
        "eventId": "a6703cc8-9e79-415d-ac03-a4dc7f6ab43c",
        "correlationId": "48fb4cd3-2ef6-4479-bea1-7c92721b988c",
        "eventType": "access.log.created",
        "timestamp": "2019-08-24T14:15:22Z",
        "source": "access-gate",
        "data": {
            "gateId": "GATE-001",
            "zoneId": "ZONE-A",
            "direction": "in",
            "personHash": "person-001"
        }
    }
]


class AlertPayload(BaseModel):
    alertType: str
    severity: str
    message: str
    source: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "analytics-integrated-service",
        "time": "2026-05-19T08:00:00Z"
    }
@app.head("/health")
def health_head():
    return None

@app.get("/telemetry")
def get_telemetry(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization, "/telemetry")
    return {
        "items": telemetry_items
    }


@app.get("/camera/motion")
def get_camera_motion(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization, "/camera/motion")
    return {
        "items": camera_motion_items
    }


@app.get("/policy-decisions")
def get_policy_decisions(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization, "/policy-decisions")
    return {
        "items": policy_decision_items
    }


@app.get("/access/logs")
def get_access_logs(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization, "/access/logs")
    return {
        "items": access_log_items
    }


@app.get("/events")
def get_events(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization, "/events")
    return {
        "items": telemetry_items + camera_motion_items + policy_decision_items + access_log_items
    }


@app.get("/alerts/recent")
def get_recent_alerts(
    limit: int = 10,
    authorization: Optional[str] = Header(default=None)
):
    require_auth(authorization, "/alerts/recent")

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail=problem_details(
                422,
                "Invalid limit",
                "limit must be between 1 and 100",
                "/alerts/recent"
            )
        )

    return {
        "items": []
    }


@app.get("/alerts/{alert_id}")
def get_alert_by_id(
    alert_id: UUID,
    authorization: Optional[str] = Header(default=None)
):
    require_auth(authorization, f"/alerts/{alert_id}")

    raise HTTPException(
        status_code=404,
        detail=problem_details(
            404,
            "Alert not found",
            "The requested alert does not exist",
            f"/alerts/{alert_id}"
        )
    )


@app.post("/alerts", status_code=201)
def create_alert(
    payload: AlertPayload,
    authorization: Optional[str] = Header(default=None)
):
    require_auth(authorization, "/alerts")

    if payload.severity not in ["low", "medium", "high", "critical"]:
        raise HTTPException(
            status_code=422,
            detail=problem_details(
                422,
                "Invalid alert payload",
                "severity must be one of low, medium, high, critical",
                "/alerts"
            )
        )

    return {
        "alertId": "alert-001",
        "accepted": True,
        "message": "Alert accepted"
    }
