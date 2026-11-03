import { WeatherAlertCertainty, WeatherAlertSourceType, WeatherAlertStatus, WeatherAlertUrgency } from '../weatherAlertEnums';
it('keeps weather lifecycle, urgency, certainty and source values aligned with Core', () => {
  expect([0, 1, 2, 3].map((value) => WeatherAlertStatus[value])).toEqual(['Active', 'Updated', 'Expired', 'Cancelled']);
  expect([0, 1, 2, 3, 4].map((value) => WeatherAlertUrgency[value])).toEqual(['Immediate', 'Expected', 'Future', 'Past', 'Unknown']);
  expect([0, 1, 2, 3, 4].map((value) => WeatherAlertCertainty[value])).toEqual(['Observed', 'Likely', 'Possible', 'Unlikely', 'Unknown']);
  expect([0, 1, 2].map((value) => WeatherAlertSourceType[value])).toEqual(['NWS', 'EnvironmentCanada', 'MeteoAlarm']);
});
