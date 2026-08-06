import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../models/wallpaper.dart';

/// App store link constants placeholder.
abstract final class StoreConstants {
  static const String playStoreUrl =
      'https://play.google.com/store/apps/details?id=com.wallpaper.gallery';
  static const String appStoreUrl =
      'https://apps.apple.com/app/wallpaper-gallery/id000000000';
}

/// Service interface for native platform sharing.
abstract interface class IShareService {
  Future<bool> shareWallpaper(Wallpaper wallpaper);
  Future<bool> shareApp();
}

/// Production implementation of [IShareService] using [SharePlus] and [path_provider].
final class LocalShareService implements IShareService {
  const LocalShareService();

  @override
  Future<bool> shareWallpaper(Wallpaper wallpaper) async {
    try {
      final ByteData byteData = await rootBundle.load(wallpaper.imagePath);
      final Uint8List bytes = byteData.buffer.asUint8List(
        byteData.offsetInBytes,
        byteData.lengthInBytes,
      );

      final tempDir = await getTemporaryDirectory();
      final sanitizeName = wallpaper.id.replaceAll(RegExp(r'[^a-zA-Z0-9_]'), '_');
      final tempFile = File('${tempDir.path}/$sanitizeName.jpg');

      await tempFile.writeAsBytes(bytes, flush: true);

      final xfile = XFile(tempFile.path, mimeType: 'image/jpeg');

      final result = await SharePlus.instance.share(
        ShareParams(
          files: [xfile],
          text: 'Check out "${wallpaper.title}" from Wallpaper Gallery!',
        ),
      );

      return result.status == ShareResultStatus.success;
    } catch (_) {
      return false;
    }
  }

  @override
  Future<bool> shareApp() async {
    try {
      final result = await SharePlus.instance.share(
        ShareParams(
          text:
              'Check out Wallpaper Gallery - Premium Offline Wallpapers App!\n\nExplore high-resolution offline wallpapers anytime.',
        ),
      );
      return result.status == ShareResultStatus.success;
    } catch (_) {
      return false;
    }
  }
}
