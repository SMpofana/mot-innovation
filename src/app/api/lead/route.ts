import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, business, stage, message, source } = body;

    // Validate required fields
    if (!name || !email) {
      return NextResponse.json(
        { error: 'Name and email are required' },
        { status: 400 }
      );
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      );
    }

    // Extract UTM parameters from referrer URL if present
    const referrer = request.headers.get('referer') || '';
    let utm: Record<string, string> = {};
    try {
      if (referrer) {
        const url = new URL(referrer);
        utm = {
          utm_source: url.searchParams.get('utm_source') || '',
          utm_medium: url.searchParams.get('utm_medium') || '',
          utm_campaign: url.searchParams.get('utm_campaign') || '',
          utm_content: url.searchParams.get('utm_content') || '',
        };
      }
    } catch {
      // referrer might not be a valid URL, that's fine
    }

    // Lead data with UTM tracking
    const lead = {
      name,
      email,
      business: business || '',
      stage: stage || '',
      message: message || '',
      source: source || 'website-contact-form',
      timestamp: new Date().toISOString(),
      userAgent: request.headers.get('user-agent') || '',
      referrer,
      utm,
    };

    console.log('[M.O.T Lead Capture]', JSON.stringify(lead, null, 2));

    // Hand the lead to the Python automation pipeline when running in a local
    // dev environment where the automation/ dir is present. On Render
    // (serverless) the Python pipeline doesn't ship, so we gracefully skip.
    let pipeline: 'local' | 'skipped' = 'skipped';
    let pipelineError: string | null = null;
    try {
      const { execFile } = await import('child_process');
      const { promisify } = await import('util');
      const path = await import('path');
      const execFileAsync = promisify(execFile);

      const projectRoot = path.resolve(process.cwd());
      const automationDir = path.join(projectRoot, 'automation');
      const leadCapture = path.join(automationDir, 'lead_capture.py');

      const { existsSync } = await import('fs');
      if (existsSync(leadCapture)) {
        const payload = {
          name,
          email,
          business: business || '',
          stage: stage || '',
          message: message || '',
          source: source || 'website-contact-form',
          user_agent: request.headers.get('user-agent') || '',
          referrer,
        };
        await execFileAsync('python', [leadCapture, '--lead', JSON.stringify(payload)], {
          cwd: projectRoot,
          timeout: 15000,
        });
        pipeline = 'local';
      }
    } catch (err) {
      pipeline = 'skipped';
      pipelineError = err instanceof Error ? err.message : String(err);
      console.error('[M.O.T Lead Capture] Python pipeline not invoked:', pipelineError);
    }

    // TODO: Wire up to actual email/CRM service
    // Example with Resend:
    // await fetch('https://api.resend.com/emails', {
    //   method: 'POST',
    //   headers: {
    //     'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({
    //     from: 'leads@motinnovation.co.za',
    //     to: 'hello@motinnovation.co.za',
    //     subject: `New Lead: ${name} from ${business || 'Unknown'}`,
    //     text: `New consultation request:\n\nName: ${name}\nEmail: ${email}\nBusiness: ${business}\nStage: ${stage}\nMessage: ${message}\n\nSource: ${source}\nTime: ${lead.timestamp}`,
    //   }),
    // });

    return NextResponse.json({
      success: true,
      message: 'Lead captured successfully',
      leadId: `lead_${Date.now()}`,
      pipeline,
      ...(pipelineError ? { pipelineError } : {}),
    });
  } catch (error) {
    console.error('[Lead Capture Error]', error);
    return NextResponse.json(
      { error: 'Failed to capture lead' },
      { status: 500 }
    );
  }
}

// Also support GET for health check
export async function GET() {
  return NextResponse.json({ status: 'ok', service: 'M.O.T Innovation Lead Capture' });
}