import 'dart:io';
import 'package:flutter/services.dart';
import 'package:gal/gal.dart';
import 'package:path_provider/path_provider.dart';
import '../models/wallpaper.dart';

/// Repository interface for downloading and saving wallpapers to device gallery.
abstract interface class IDownloadRepository {
  Future<bool> hasStoragePermission();
  Future<bool> requestStoragePermission();
  Future<bool> saveWallpaperToGallery(Wallpaper wallpaper);
}

/// Production implementation of [IDownloadRepository] saving asset images via [Gal].
final class LocalDownloadRepository implements IDownloadRepository {
  const LocalDownloadRepository();

  @override
  Future<bool> hasStoragePermission() async {
    try {
      return await Gal.hasAccess(toAlbum: false);
    } catch (_) {
      return false;
    }
  }

  @override
  Future<bool> requestStoragePermission() async {
    try {
      return await Gal.requestAccess(toAlbum: false);
    } catch (_) {
      return false;
    }
  }

  @override
  Future<bool> saveWallpaperToGallery(Wallpaper wallpaper) async {
    File? tempFile;
    try {
      final ByteData byteData = await rootBundle.load(wallpaper.imagePath);
      final Uint8List bytes = byteData.buffer.asUint8List(
        byteData.offsetInBytes,
        byteData.lengthInBytes,
      );

      final sanitizeName = wallpaper.id.replaceAll(RegExp(r'[^a-zA-Z0-9_]'), '_');
      final tempDir = await getTemporaryDirectory();
      tempFile = File('${tempDir.path}/wallpaper_$sanitizeName.webp');
      await tempFile.writeAsBytes(bytes, flush: true);

      await Gal.putImage(tempFile.path);
      return true;
    } on GalException catch (e) {
      if (e.type == GalExceptionType.accessDenied) {
        return false;
      }
      return false;
    } catch (_) {
      return false;
    } finally {
      if (tempFile != null && await tempFile.exists()) {
        try {
          await tempFile.delete();
        } catch (_) {}
      }
    }
  }
}
