import math
import uuid

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Building


class BuildingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, building_id: uuid.UUID) -> Building | None:
        return self._session.get(Building, building_id)

    def get_all(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Building]:
        q = select(Building).order_by(Building.address).limit(limit).offset(offset)
        return list(self._session.scalars(q).all())

    def get_ids_in_bbox(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
    ) -> list[uuid.UUID]:
        q = select(Building.id).where(
            and_(
                Building.latitude >= lat_min,
                Building.latitude <= lat_max,
                Building.longitude >= lon_min,
                Building.longitude <= lon_max,
            )
        )
        return list(self._session.scalars(q).all())

    def get_ids_in_radius(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[uuid.UUID]:
        # Approximate: 1 deg lat ~ 111 km, 1 deg lon ~ 111*cos(lat) km
        # Bbox for filtering, then exact haversine in Python (or use PostGIS in real prod)
        deg_lat = radius_m / 111_320
        deg_lon = radius_m / (111_320 * max(0.01, math.cos(math.radians(lat))))
        lat_min, lat_max = lat - deg_lat, lat + deg_lat
        lon_min, lon_max = lon - deg_lon, lon + deg_lon
        q = select(Building).where(
            and_(
                Building.latitude >= lat_min,
                Building.latitude <= lat_max,
                Building.longitude >= lon_min,
                Building.longitude <= lon_max,
            )
        )
        buildings = list(self._session.scalars(q).all())
        # Haversine filter
        result = []
        for b in buildings:
            d = _haversine_m(lat, lon, b.latitude, b.longitude)
            if d <= radius_m:
                result.append(b.id)
        return result


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000  # metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
