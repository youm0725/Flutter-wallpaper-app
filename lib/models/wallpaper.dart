import 'package:flutter/foundation.dart';

/// Immutable model representing a single wallpaper item in the gallery.
@immutable
final class Wallpaper {
  final String id;
  final String title;
  final String category;
  final String imagePath;
  final String? thumbnailPath;
  final String resolution;
  final String fileSize;
  final List<String> tags;
  final bool isFeatured;
  final List<String> collections;
  final String description;

  const Wallpaper({
    required this.id,
    required this.title,
    required this.category,
    required this.imagePath,
    this.thumbnailPath,
    required this.resolution,
    required this.fileSize,
    required this.tags,
    this.isFeatured = false,
    this.collections = const <String>[],
    this.description = '',
  });

  /// Returns thumbnail path if specified, falling back to full image path.
  String get effectiveThumbnailPath =>
      (thumbnailPath != null && thumbnailPath!.isNotEmpty)
          ? thumbnailPath!
          : imagePath;

  /// Factory constructor to create a [Wallpaper] from a JSON map.
  factory Wallpaper.fromJson(Map<String, dynamic> json) {
    final rawFeatured = json['isFeatured'] ?? json['featured'];
    return Wallpaper(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      category: json['category'] as String? ?? '',
      imagePath: json['imagePath'] as String? ?? '',
      thumbnailPath: json['thumbnailPath'] as String?,
      resolution: json['resolution'] as String? ?? '1080x1920',
      fileSize: json['fileSize'] as String? ?? '',
      tags: (json['tags'] as List<dynamic>?)
              ?.map((dynamic tag) => tag.toString())
              .toList() ??
          const <String>[],
      isFeatured: rawFeatured is bool ? rawFeatured : false,
      collections: (json['collections'] as List<dynamic>?)
              ?.map((dynamic c) => c.toString())
              .toList() ??
          const <String>[],
      description: json['description'] as String? ?? '',
    );
  }

  /// Converts this [Wallpaper] instance to a JSON map.
  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'title': title,
      'category': category,
      'imagePath': imagePath,
      if (thumbnailPath != null) 'thumbnailPath': thumbnailPath,
      'resolution': resolution,
      'fileSize': fileSize,
      'tags': tags,
      'isFeatured': isFeatured,
      'collections': collections,
      'description': description,
    };
  }

  /// Creates a copy of this [Wallpaper] with updated values.
  Wallpaper copyWith({
    String? id,
    String? title,
    String? category,
    String? imagePath,
    String? thumbnailPath,
    String? resolution,
    String? fileSize,
    List<String>? tags,
    bool? isFeatured,
    List<String>? collections,
    String? description,
  }) {
    return Wallpaper(
      id: id ?? this.id,
      title: title ?? this.title,
      category: category ?? this.category,
      imagePath: imagePath ?? this.imagePath,
      thumbnailPath: thumbnailPath ?? this.thumbnailPath,
      resolution: resolution ?? this.resolution,
      fileSize: fileSize ?? this.fileSize,
      tags: tags ?? this.tags,
      isFeatured: isFeatured ?? this.isFeatured,
      collections: collections ?? this.collections,
      description: description ?? this.description,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is Wallpaper &&
        other.id == id &&
        other.title == title &&
        other.category == category &&
        other.imagePath == imagePath &&
        other.thumbnailPath == thumbnailPath &&
        other.resolution == resolution &&
        other.fileSize == fileSize &&
        other.isFeatured == isFeatured &&
        other.description == description &&
        listEquals(other.tags, tags) &&
        listEquals(other.collections, collections);
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      title,
      category,
      imagePath,
      thumbnailPath,
      resolution,
      fileSize,
      isFeatured,
      description,
      Object.hashAll(tags),
      Object.hashAll(collections),
    );
  }

  @override
  String toString() {
    return 'Wallpaper(id: $id, title: $title, category: $category, imagePath: $imagePath, thumbnailPath: $thumbnailPath, resolution: $resolution, fileSize: $fileSize, tags: $tags, isFeatured: $isFeatured, collections: $collections, description: $description)';
  }
}
