import 'package:flutter/material.dart';
import '../../core/constants/app_info.dart';
import '../../core/constants/app_sizes.dart';

/// Privacy Policy screen — structured, readable, fully offline content.
class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Privacy Policy')),
      body: SafeArea(
        child: ListView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(AppSizes.p16),
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(AppSizes.p16),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
              child: Row(
                children: [
                  Icon(Icons.privacy_tip_rounded,
                      color: theme.colorScheme.primary, size: AppSizes.iconMd),
                  const SizedBox(width: AppSizes.p12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Your Privacy Matters',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                        const SizedBox(height: AppSizes.p2),
                        Text(
                          'Last updated: January 2025',
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppSizes.p24),

            // Privacy sections
            ...PrivacyContent.sections.map(
              (section) => _LegalSection(
                heading: section.heading,
                body: section.body,
              ),
            ),

            const SizedBox(height: AppSizes.p32),
          ],
        ),
      ),
    );
  }
}

/// Terms & Conditions screen — structured content, easy to update via [TermsContent].
class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Terms & Conditions')),
      body: SafeArea(
        child: ListView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(AppSizes.p16),
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(AppSizes.p16),
              decoration: BoxDecoration(
                color: theme.colorScheme.secondaryContainer.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
              child: Row(
                children: [
                  Icon(Icons.gavel_rounded,
                      color: theme.colorScheme.secondary, size: AppSizes.iconMd),
                  const SizedBox(width: AppSizes.p12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Terms & Conditions',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                            color: theme.colorScheme.secondary,
                          ),
                        ),
                        const SizedBox(height: AppSizes.p2),
                        Text(
                          'Last updated: January 2025',
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppSizes.p24),

            // Terms sections
            ...TermsContent.sections.map(
              (section) => _LegalSection(
                heading: section.heading,
                body: section.body,
              ),
            ),

            const SizedBox(height: AppSizes.p32),
          ],
        ),
      ),
    );
  }
}

// ── Shared Private Widget ────────────────────────────────────────────────────

class _LegalSection extends StatelessWidget {
  final String heading;
  final String body;

  const _LegalSection({required this.heading, required this.body});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSizes.p20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            heading,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: -0.2,
            ),
          ),
          const SizedBox(height: AppSizes.p6),
          Text(
            body,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
}
