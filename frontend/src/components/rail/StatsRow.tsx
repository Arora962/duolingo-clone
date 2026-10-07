"use client";

import HoverCard from "@/components/rail/HoverCard";
import StatPill from "@/components/rail/StatPill";
import {
  CoursesPopover,
  GemsPopover,
  HeartsPopover,
  STREAK_HEADER_CLASS,
  StreakPopover,
} from "@/components/rail/StatPopovers";
import DuoAsset from "@/components/shared/duoAssets";
import type { UserProfile } from "@/lib/types";

/**
 * The stats strip at the top of the rail.
 *
 * Course, XP, streak, gems, and hearts are shown as separate stats so the
 * desktop rail matches the same information hierarchy as the responsive top
 * bar. Each stat opens its existing popover on hover/focus.
 */
export default function StatsRow({
  user,
  onRefillHearts,
}: {
  user: UserProfile;
  /** Instant heart refill, owned by the rail so the profile can refresh after. */
  onRefillHearts: () => void;
}) {
  return (
    <div className="mb-2 flex items-center justify-between">
      <HoverCard label="Your courses" align="left" trigger={
        <div className="flex items-center rounded-xl py-1 pl-[10px] pr-2">
          <DuoAsset name="flag" />
        </div>
      }>
        <CoursesPopover />
      </HoverCard>

      <HoverCard label="Your XP" trigger={
        <StatPill
          icon={<DuoAsset name="questBolt" height={25} />}
          value={user.xp_total}
          label="XP"
          valueClassName="text-duo-blue"
        />
      }>
        <div className="px-4 py-3 text-sm font-bold text-duo-text">
          Total XP: {user.xp_total}
        </div>
      </HoverCard>

      {/* The streak card's top band is amber, so its pointer matches it. */}
      <HoverCard label="Your streak" caretClassName={STREAK_HEADER_CLASS} trigger={
        <StatPill
          icon={<DuoAsset name="streak" />}
          value={user.streak_count}
          label="Day streak"
          valueClassName="text-duo-streak"
        />
      }>
        <StreakPopover user={user} />
      </HoverCard>

      <HoverCard label="Your gems" trigger={
        <StatPill
          icon={<DuoAsset name="gem" />}
          value={user.gems}
          label="Gems"
          valueClassName="text-duo-gemText"
          target="gems"
        />
      }>
        <GemsPopover user={user} />
      </HoverCard>

      <HoverCard label="Your hearts" align="right" trigger={
        <StatPill
          icon={<DuoAsset name="heart" />}
          value={user.hearts}
          label={`Hearts out of ${user.max_hearts}`}
          valueClassName="text-duo-heartText"
        />
      }>
        <HeartsPopover user={user} onRefill={onRefillHearts} />
      </HoverCard>
    </div>
  );
}
