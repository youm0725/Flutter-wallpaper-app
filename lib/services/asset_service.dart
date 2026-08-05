import 'package:flutter/services.dart';

/// Contract for loading local bundle assets.
abstract interface class IAssetService {
  Future<String> loadString(String path);
}

/// Production implementation of [IAssetService] using Flutter's [rootBundle].
final class AssetBundleService implements IAssetService {
  final AssetBundle _bundle;

  AssetBundleService({AssetBundle? bundle})
      : _bundle = bundle ?? rootBundle;

  @override
  Future<String> loadString(String path) async {
    return await _bundle.loadString(path);
  }
}
