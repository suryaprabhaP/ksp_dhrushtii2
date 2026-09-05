import React from 'react';
import ComplaintPortal from '../../ComplaintPortal';

/**
 * ComplaintPortalContainer bridges the e-Complaint portal view into the main dashboard.
 * Uses the DRISHTI Warm Parchment themed Citizen E-Complaint Module.
 */
export default function ComplaintPortalContainer({ onBackToDashboard }) {
  return (
    <ComplaintPortal
      onBackToDashboard={onBackToDashboard}
      onClose={onBackToDashboard}
    />
  );
}