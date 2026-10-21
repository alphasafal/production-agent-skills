# Feature brief: Team invitations

**Owner:** Priya (Product) · **Target:** start sprint 14 · **Status:** approved for build

## Problem

Today the only way to get a teammate into a Fieldnote workspace is for them
to sign up on their own and then message the workspace owner, who adds them
by user ID from the admin panel. In last quarter's churn interviews, 7 of 19
churned teams said "getting the rest of the team in was a pain." Workspaces
that reach 3+ active members in week one retain at roughly twice the rate of
single-user workspaces.

## What we want

Workspace owners and admins can invite teammates by email from the Members
page. They pick a role for each person when they send the invite. The
invitee gets an email with a link; clicking it drops them into the workspace
with the role they were given.

- Invite one or more people at once — paste a list of emails, comma or
  newline separated.
- Pick the role per invite: admin, member, or viewer. Billing admins should
  also get a heads-up email whenever someone new joins, since they're the
  ones who see the invoice.
- The Members page shows pending invites alongside current members, with
  the option to resend or revoke a pending invite.
- Invite links shouldn't work forever.
- Invited people should be able to get in with as little friction as
  possible — we don't want a separate sign-up step to be the thing that
  loses them.

## Also

While we're in here, it'd be great to also let people request to join a
workspace: if someone signs up with an `@acme.com` address and an Acme
workspace exists, they could hit "Request to join" and an admin approves
them. Sales has been asking for this for the enterprise pilots.

## Success metrics

- % of new workspaces with 3+ members by day 7 goes from 18% to 30%.
- Invite acceptance rate above 50%.

## Out of scope

- SSO / SCIM provisioning.
- Inviting people to a single project instead of a whole workspace.

## Notes

- Design has mocks for the Members page and the invite modal (Figma link in
  the ticket).
- Free, Team and Business plans all get invitations.
