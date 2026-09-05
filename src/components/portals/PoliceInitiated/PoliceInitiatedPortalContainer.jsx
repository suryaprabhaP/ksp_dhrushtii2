import React from 'react';
import PoliceInitiatedComplaintPortal from '../../PoliceInitiatedComplaintPortal';

/**
 * PoliceInitiatedPortalContainer bridges the police-initiated complaint view into the main dashboard.
 * Uses the DRISHTI Warm Parchment themed Suo-Moto FIR Module.
 */
export default function PoliceInitiatedPortalContainer({ onBackToDashboard }) {
  return (
    <PoliceInitiatedComplaintPortal
      onBackToDashboard={onBackToDashboard}
      onClose={onBackToDashboard}
    />
  );
}