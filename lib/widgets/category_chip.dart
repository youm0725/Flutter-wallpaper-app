import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';

/// Reusable, refined category filter chip.
class CategoryChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const CategoryChip({
    super.key,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final backgroundColor = isSelected
        ? theme.colorScheme.primary
        : isDark
            ? theme.colorScheme.surfaceContainerHighest
            : theme.colorScheme.surface;

    final foregroundColor = isSelected
        ? theme.colorScheme.onPrimary
        : theme.colorScheme.onSurfaceVariant;

    final borderColor = isSelected
        ? theme.colorScheme.primary
        : theme.colorScheme.outline.withValues(alpha: 0.3);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      curve: Curves.easeInOut,
      margin: const EdgeInsets.only(right: AppSizes.p8),
      child: Material(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(AppSizes.radiusSm + 2),
        elevation: isSelected ? 1 : 0,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppSizes.radiusSm + 2),
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSizes.p16,
              vertical: AppSizes.p8,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(AppSizes.radiusSm + 2),
              border: Border.all(
                color: borderColor,
                width: 1.0,
              ),
            ),
            child: Center(
              child: Text(
                label,
                style: theme.textTheme.labelMedium?.copyWith(
                  color: foregroundColor,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                  letterSpacing: 0.2,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
