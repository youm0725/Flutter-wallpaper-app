import 'package:flutter/foundation.dart';

/// Immutable model representing a single wallpaper item.
@immutable
final class Wallpaper {
  final String id;
  final String title;
  final String category;
  final String imagePath;
  final String resolution;
  final String fileSize;
  final List<String> tags;

  const Wallpaper({
    required this.id,
    required this.title,
    required this.category,
    required this.imagePath,
    required this.resolution,
    required this.fileSize,
    required this.tags,
  });

  /// Factory constructor to create a [Wallpaper] from a JSON map.
  factory Wallpaper.fromJson(Map<String, dynamic> json) {
    return Wallpaper(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      category: json['category'] as String? ?? '',
      imagePath: json['imagePath'] as String? ?? '',
      resolution: json['resolution'] as String? ?? '',
      fileSize: json['fileSize'] as String? ?? '',
      tags: (json['tags'] as List<dynamic>?)
              ?.map((dynamic tag) => tag.toString())
              .toList() ??
          const <String>[],
    );
  }

  /// Converts this [Wallpaper] instance to a JSON map.
  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'title': title,
      'category': category,
      'imagePath': imagePath,
      'resolution': resolution,
      'fileSize': fileSize,
      'tags': tags,
    };
  }

  /// Creates a copy of this [Wallpaper] with updated values.
  Wallpaper copyWith({
    String? id,
    String? title,
    String? category,
    String? imagePath,
    String? resolution,
    String? fileSize,
    List<String>? tags,
  }) {
    return Wallpaper(
      id: id ?? this.id,
      title: title ?? this.title,
      category: category ?? this.category,
      imagePath: imagePath ?? this.imagePath,
      resolution: resolution ?? this.resolution,
      fileSize: fileSize ?? this.fileSize,
      tags: tags ?? this.tags,
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
        other.resolution == resolution &&
        other.fileSize == fileSize &&
        listEquals(other.tags, tags);
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      title,
      category,
      imagePath,
      resolution,
      fileSize,
      Object.hashAll(tags),
    );
  }

  @override
  String toString() {
    return 'Wallpaper(id: $id, title: $title, category: $category, imagePath: $imagePath, resolution: $resolution, fileSize: $fileSize, tags: $tags)';
  }
}
