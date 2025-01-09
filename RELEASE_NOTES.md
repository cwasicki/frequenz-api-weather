# Frequenz Weather API Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- The minimum required version of `frequenz-client-base` is now `v0.8.0`.

- The `Client` now expects gRPC URLs to be [this format](https://frequenz-floss.github.io/frequenz-client-base-python/latest/reference/frequenz/client/base/channel/#frequenz.client.base.channel.parse_grpc_uri) required by the `BaseApiClient`.

## New Features

* Add a new tool to request historical weather data from the command line.
  After installing the package, the `weather-cli` command can be used to
  request historical weather data for user-defined parameters.
  Replaces the historical forecast example.


<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
