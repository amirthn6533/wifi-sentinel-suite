import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from wifi_radar import KalmanFilter1D, MacVendorLookup, SecurityAuditor

def test_kalman_filter_initialization():
    kf = KalmanFilter1D(initial_value=-50.0)
    filtered = kf.update(-50.0)
    assert filtered == -50.0

def test_kalman_filter_smoothing():
    kf = KalmanFilter1D(process_variance=0.1, measurement_variance=4.0, initial_value=-60.0)
    kf.update(-60.0)
    smoothed = kf.update(-30.0)
    assert smoothed < -50.0

def test_mac_vendor_lookup():
    assert MacVendorLookup.lookup("50:D4:F7:11:22:33") == "TP-Link"
    assert MacVendorLookup.lookup("00:E0:FC:AA:BB:CC") == "Huawei"
    assert MacVendorLookup.lookup("00:00:00:00:00:00") == "Generic Vendor"

def test_security_auditor_open():
    audit = SecurityAuditor.audit_network({'auth': 'OPEN', 'encryption': 'NONE'})
    assert audit['risk_code'] == 'CRITICAL'
    assert audit['is_insecure'] is True

def test_security_auditor_wpa3():
    audit = SecurityAuditor.audit_network({'auth': 'WPA3-SAE', 'encryption': 'CCMP'})
    assert audit['risk_code'] == 'SECURE'
    assert audit['is_insecure'] is False
