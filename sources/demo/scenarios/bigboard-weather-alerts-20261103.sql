-- Fictional display-only alerts for Academy screen recordings. No provider poll or message delivery.
BEGIN;
DO $$
BEGIN
  IF current_database() <> 'resgrid_academy' OR NOT EXISTS (
    SELECT 1 FROM departments WHERE departmentid=51 AND name='Firehouse 51 — Training Department'
  ) THEN RAISE EXCEPTION 'This fixture is restricted to the Academy training database'; END IF;
  IF NOT EXISTS (SELECT 1 FROM weatheralertsources WHERE weatheralertsourceid='6a077c32-6c76-4650-bdc2-e26a2c0fdd9b' AND departmentid=51 AND active=false)
    THEN RAISE EXCEPTION 'The fictional source must exist and remain inactive'; END IF;
END $$;
INSERT INTO weatheralerts (weatheralertid,departmentid,weatheralertsourceid,externalid,sender,event,alertcategory,severity,urgency,certainty,status,headline,description,instruction,areadescription,centergeolocation,effectiveutc,expiresutc,firstseenutc,lastupdatedutc,notificationsent)
SELECT fixture.id,51,'6a077c32-6c76-4650-bdc2-e26a2c0fdd9b',fixture.externalid,'TRAINING ONLY - Academy fixture',fixture.event,fixture.category,fixture.severity,1,2,fixture.status,fixture.headline,
'TRAINING ONLY - Fictional software exercise. This is not a weather-provider bulletin.',
'TRAINING ONLY - Review the example detail and your department procedures. No real response is requested.',
'TRAINING ONLY - Chicago community exercise area','41.85,-87.69',timezone('UTC',CURRENT_TIMESTAMP)-interval '5 minutes',
CASE WHEN fixture.status=2 THEN timezone('UTC',CURRENT_TIMESTAMP)-interval '1 hour' ELSE timezone('UTC',CURRENT_TIMESTAMP)+interval '6 hours' END,
timezone('UTC',CURRENT_TIMESTAMP),timezone('UTC',CURRENT_TIMESTAMP),true
FROM (VALUES
('b9170511-8f12-4b2a-8261-d9e007020001','academy-weather-severe-20261103','TRAINING ONLY - Severe weather exercise',0,1,0,'TRAINING ONLY - Review an outdoor standby weather scenario'),
('b9170511-8f12-4b2a-8261-d9e007020002','academy-weather-health-20261103','TRAINING ONLY - Heat outreach exercise',2,2,0,'TRAINING ONLY - Community outreach planning example'),
('b9170511-8f12-4b2a-8261-d9e007020003','academy-weather-minor-20261103','TRAINING ONLY - Environmental exercise',3,3,0,'TRAINING ONLY - Industrial site planning example'),
('b9170511-8f12-4b2a-8261-d9e007020004','academy-weather-expired-20261103','TRAINING ONLY - Ended weather exercise',0,2,2,'TRAINING ONLY - Historical software exercise')
) fixture(id,externalid,event,category,severity,status,headline)
ON CONFLICT (weatheralertid) DO NOTHING;
SELECT event,severity,alertcategory,status,notificationsent FROM weatheralerts WHERE externalid LIKE 'academy-weather-%-20261103' ORDER BY externalid;
COMMIT;
