from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from app.routes import analyse_tracking_points

BASE = datetime(2026, 9, 16, 6, 0, tzinfo=timezone.utc)

def point(i, lat, lon, speed=20, accuracy=10, sampled_at=None):
    return SimpleNamespace(id=i, latitude=lat, longitude=lon, speed_kmh=speed,
                           accuracy_m=accuracy, sampled_at=sampled_at or BASE + timedelta(seconds=i * 10))

def test_continuous_measured_route():
    result = analyse_tracking_points([point(i, -26.6598 + i * 0.0001, 27.8250, 4, 10) for i in range(6)])
    assert len(result['segments']) == 1
    assert len(result['points']) == 6
    assert result['distance_km'] > 0

def test_stationary_jitter_does_not_create_route_or_stops():
    result = analyse_tracking_points([point(i, -26.6598 + (i % 2) * 0.00001, 27.8250, 0, 15) for i in range(20)])
    assert result['segments'] == []
    assert result['distance_km'] == 0
    assert result['stopped_minutes'] == 0
    assert result['stops'] == []

def test_impossible_jump_is_not_connected():
    result = analyse_tracking_points([point(0, -26.6598, 27.8250), point(1, -26.2, 28.2)])
    assert result['rejection_counts']['IMPOSSIBLE_JUMP'] == 1
    assert result['distance_km'] == 0

def test_three_minute_gap_is_not_joined():
    rows = [point(0, -26.6598, 27.8250), point(1, -26.6597, 27.8250),
            point(2, -26.6596, 27.8250, sampled_at=BASE + timedelta(minutes=10))]
    result = analyse_tracking_points(rows)
    assert len(result['segments']) == 1

def test_poor_accuracy_is_rejected():
    result = analyse_tracking_points([point(0, -26.6598, 27.8250, accuracy=180), point(1, -26.6597, 27.8250)])
    assert result['rejection_counts']['POOR_ACCURACY'] == 1

def test_stop_requires_prior_movement_and_two_minutes():
    rows = [point(0, -26.6598, 27.8250, 15), point(1, -26.6597, 27.8250, 15),
            point(2, -26.6596, 27.8250, 15),
            point(3, -26.6596, 27.8250, 0, sampled_at=BASE + timedelta(seconds=40)),
            point(4, -26.6596, 27.8250, 0, sampled_at=BASE + timedelta(seconds=190)),
            point(5, -26.6595, 27.8250, 15, sampled_at=BASE + timedelta(seconds=200))]
    result = analyse_tracking_points(rows)
    assert len(result['stops']) == 1
    assert result['stopped_minutes'] >= 2

def test_normal_highway_distance_over_250m_is_accepted():
    rows = [
        point(0, -26.7000, 27.9000, 100, 10, BASE),
        point(1, -26.6964, 27.9000, 100, 10, BASE + timedelta(seconds=15)),
        point(2, -26.6928, 27.9000, 100, 10, BASE + timedelta(seconds=30)),
    ]
    result = analyse_tracking_points(rows)
    assert result['rejection_counts'].get('IMPOSSIBLE_JUMP', 0) == 0
    assert len(result['journeys']) == 1
    assert result['distance_km'] > 0.7


def test_five_minute_mobile_reporting_gap_keeps_one_journey():
    rows = [
        point(0, -26.7000, 27.9000, 70, 10, BASE),
        point(1, -26.6990, 27.9000, 70, 10, BASE + timedelta(seconds=15)),
        point(2, -26.6500, 27.9000, 70, 10, BASE + timedelta(minutes=5, seconds=15)),
        point(3, -26.6490, 27.9000, 70, 10, BASE + timedelta(minutes=5, seconds=30)),
    ]
    result = analyse_tracking_points(rows)
    assert len(result['journeys']) == 1
    assert result['distance_km'] > 5


def test_short_customer_stop_does_not_split_journey():
    rows = [
        point(0, -26.7000, 27.9000, 30, 8, BASE),
        point(1, -26.6990, 27.9000, 30, 8, BASE + timedelta(seconds=30)),
        point(2, -26.6990, 27.9000, 0, 8, BASE + timedelta(minutes=1)),
        point(3, -26.6990, 27.9000, 0, 8, BASE + timedelta(minutes=6)),
        point(4, -26.6980, 27.9000, 30, 8, BASE + timedelta(minutes=6, seconds=30)),
        point(5, -26.6970, 27.9000, 30, 8, BASE + timedelta(minutes=7)),
    ]
    result = analyse_tracking_points(rows)
    assert len(result['journeys']) == 1
    assert result['stopped_minutes'] >= 5
