from app.services.report_service import ReportService

def main():
    rs = ReportService()
    aid = 'audit_SSH_Penetration_Testing_20260404_232301'
    md = rs.get_report_file_path(aid, 'md')
    js = rs.get_report_file_path(aid, 'json')
    print('md:', md, 'exists' if md and md.exists() else 'not found')
    print('json:', js, 'exists' if js and js.exists() else 'not found')

if __name__ == '__main__':
    main()
