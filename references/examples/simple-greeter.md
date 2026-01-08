# Example Skill: Simple Greeter

A minimal working skill example demonstrating core skill structure.

## Skill Overview

| Property | Value |
|----------|-------|
| Name | `simple-greeter` |
| Type | Guide |
| Complexity | Minimal |
| Files | 1 (SKILL.md only) |

## Complete SKILL.md

```markdown
---
name: simple-greeter
description: Generate friendly, personalized greetings for any occasion
version: 1.0.0
author: Skill Generator
tags: [guide, greeting, simple]
---

# Simple Greeter

Generate friendly, personalized greetings for various occasions.

## What This Skill Does

Creates customized greeting messages based on:
- Recipient name
- Occasion (birthday, holiday, thank you, etc.)
- Tone (formal, casual, playful)

## How to Use

Simply invoke the skill and provide context:

```
/simple-greeter
```

Then specify:
1. Who the greeting is for
2. What occasion
3. Preferred tone

## Greeting Templates

### Birthday

**Casual:**
> Happy Birthday, {name}! Hope your day is filled with joy and cake!

**Formal:**
> Wishing you a wonderful birthday, {name}. May this year bring you happiness and success.

### Thank You

**Casual:**
> Hey {name}, thanks so much! You're the best!

**Formal:**
> Dear {name}, I wanted to express my sincere gratitude for your kindness.

### Holiday

**Casual:**
> Happy Holidays, {name}! Have an amazing time!

**Formal:**
> Season's Greetings, {name}. Wishing you joy and peace this holiday season.

### Congratulations

**Casual:**
> Way to go, {name}! So proud of you!

**Formal:**
> Congratulations, {name}. Your achievement is truly commendable.

## Examples

### Example 1: Casual Birthday Greeting

**Request:**
```
Create a birthday greeting for my friend Alex
```

**Response:**
```
Happy Birthday, Alex! 🎂

Hope your special day is absolutely amazing! Here's to another
year of adventures, laughter, and all the good things life has
to offer. You deserve the best!

Cheers to you! 🎉
```

### Example 2: Formal Thank You

**Request:**
```
Write a formal thank you message for my manager Sarah
```

**Response:**
```
Dear Sarah,

I wanted to take a moment to express my sincere appreciation
for your guidance and support. Your mentorship has been
invaluable to my professional growth.

Thank you for believing in me and providing opportunities
to develop my skills.

With gratitude,
[Your name]
```

### Example 3: Holiday Greeting

**Request:**
```
Holiday greeting for the whole team, keep it fun
```

**Response:**
```
Happy Holidays, Team! 🎄✨

What an incredible year it's been! Thanks to each of you for
making this team so amazing. Here's to rest, relaxation, and
recharging for an even better year ahead!

Enjoy the festivities! 🥳
```

## Customization Tips

- **Add personal touches**: Mention shared experiences or inside jokes
- **Match the relationship**: Adjust formality based on your connection
- **Keep it genuine**: Authenticity matters more than fancy words
- **Consider length**: Short and sweet often works best

## Output Format

Greetings are provided as ready-to-use text that you can:
- Copy directly into messages
- Modify to add personal details
- Use as inspiration for your own words
```

## Why This Example Works

### Minimal Structure
- Single SKILL.md file (no references needed)
- Under 500 tokens
- Self-contained

### Clear Purpose
- Obvious use case
- Immediate value
- Easy to understand

### Good Examples
- Multiple scenarios
- Varied complexity
- Copy-paste ready

### Follows Best Practices
- Valid YAML frontmatter
- Descriptive sections
- Actionable guidance

## File Structure

```
simple-greeter/
└── SKILL.md    # Complete skill (432 tokens)
```

## Token Analysis

| Section | Tokens |
|---------|--------|
| Frontmatter | 45 |
| Overview | 82 |
| Templates | 156 |
| Examples | 124 |
| Tips | 25 |
| **Total** | **432** |

## Installation

```bash
# Copy to user skills
cp -r simple-greeter ~/.claude/skills/

# Or project skills
cp -r simple-greeter ./.claude/skills/
```

## Usage After Installation

```
/simple-greeter

Create a birthday greeting for my colleague Jamie who loves coffee
```

## Key Takeaways

1. **Keep it simple**: Not every skill needs references
2. **Examples matter**: Show don't just tell
3. **Be practical**: Ready-to-use output wins
4. **Stay focused**: One clear purpose per skill
