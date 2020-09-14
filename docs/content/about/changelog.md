# NetAPI Change History

## 0.2.2

New objects:

- `RoutesBase`: Collection of route objects

Refactoring:

- All active objects (except the device connector) have the Parse class refactored to be
more modular on EOS and also improved their Builder factories.

## 0.2.0

New objects:

- `FactsBase` (and development done for EOS)
- `RouteBase` (and development done for EOS)
- Usage of the following external libraries for convenience:

    - `pydantic` For objects definitions ease of validation
    - `pendulum` For ease of manupulation of `datetime` objects, calculation and timezone transformation among many other things... Take a look at their [docs](https://pendulum.eustace.io/)
    - `bitmath` For ease of manipulation to objects related to Bytes, MegaBytes, etc... Take a look at their [docs](https://bitmath.readthedocs.io/en/latest/)

Refactoring:

- `InterfaceBase` to be pydantic
- `PingBase` to be pydantic

## 0.1.0

Initial release
